import logging
import json
import requests as req
import re

from utils.struct_validate import *
from threading import Thread
from .exceptions import *
from time import sleep

from pyprometheus.registry import BaseRegistry
from pyprometheus import LocalMemoryStorage
from pyprometheus.utils.exposition import registry_to_text
from pyprometheus import Gauge

class Colector(object):
    CONTJOB_TEMPLATE = "cronjob-{}"
    TIME_BETWEEN_ITERS = 5
    API_PREFIX_GET_PODS = "api/v1/namespaces/viamais-sync/pods"
    API_POSTFIX_GET_LOGS = "{}/log?tailLines=0&follow=true"
    HEADERS={"Accept": "application/json","Authorization":"Bearer {}"}
    REGEX_TEMPLATE_CAPT_METRCIS = "^.*{} METRICS: {}:"
    METRIC_TYPES = ["cur","max","min"]
    TEMPLATE_METRIC_KEY = "{}_{}_{} {}"

    def __init__(self,*args,**kwargs):

        self.__dict__["config"] = kwargs
        self.HEADERS["Authorization"] = self.HEADERS["Authorization"].format(self.config["token"])
        self.__dict__["metrics"] = {"times_write":{},"times_read":{}}
        self.__dict__["registry"] = BaseRegistry(storage=LocalMemoryStorage())
        logging.getLogger(__name__)

    def consolidate(self,index,context,line):
        for id_regex in context:
            for id_timer in line:
                value = line[id_timer]["executionTime"]
                if re.search(id_regex,id_timer) is not None:
                    for time_type in self.METRIC_TYPES:
                        if time_type in context[id_regex]:
                            str_regex = id_regex.replace(".","_")
                            if id_regex not in self.metrics[index]:
                                self.metrics[index][id_regex] = {
                                                        "cur":Gauge("cur_{}_{}".format(index,str_regex),"current metrics from {}".format(str_regex),registry=self.registry),
                                                        "min":[Gauge("min_{}_{}".format(index,str_regex),"minimal metrics from {}".format(str_regex),registry=self.registry),None],
                                                        "max":[Gauge("max_{}_{}".format(index,str_regex),"maximun metrics from {}".format(str_regex),registry=self.registry),0]
                                                    }
                            if time_type == "cur":
                                self.metrics[index][id_regex]["cur"].set(value)
                            if time_type == "max":
                                if self.metrics[index][id_regex]["max"][1] < value:
                                    self.metrics[index][id_regex]["max"][1] = value
                                    self.metrics[index][id_regex]["max"][0].set(value)
                            if time_type == "min":
                                if self.metrics[index][id_regex]["min"][1] is None or self.metrics[index][id_regex]["min"][1] > value:
                                    self.metrics[index][id_regex]["min"][1] = value
                                    self.metrics[index][id_regex]["min"][0].set(value)

    def consolidTimeWrite(self,context,line):
        index = "times_write"
        self.consolidate(index,context[index],line[index])

    def consolidTimeRead(self,context,line):
        index = "times_read"
        self.consolidate(index,context[index],line[index])


    def collect(self):
        threads = {}
        while True:
            try:
                pods = req.get("{}/{}".format(self.config["endpoint"],self.API_PREFIX_GET_PODS),headers=self.HEADERS,verify=False)
                pods = json.loads(pods.content)
                validateStruct({"items":[{"metadata":{},"spec":{},"status":{}}]},pods)
                for pod in pods["items"]:
                    try:
                        if pod["metadata"]["labels"]["parent"] == self.CONTJOB_TEMPLATE.format(self.config["name"]) and pod["status"]["phase"] == "Running":
                            break
                        pod = None
                        continue
                    except KeyError:
                        pod = None
                        continue
                if pod is None:
                    logging.info("WAITING FOR POD FROM CRONJOB {}".format(self.config["name"]))
                    raise ForceSleep()

                logging.info("POD FROM CRONJOB {} FOUNDED".format(self.config["name"]))
                logs = req.get(
                                "{}/{}/{}".format(
                                    self.config["endpoint"],
                                    self.API_PREFIX_GET_PODS,
                                    self.API_POSTFIX_GET_LOGS.format(pod["metadata"]["name"])),
                                    headers=self.HEADERS,verify=False,stream=True)
                logging.info("RECEIVING LOG LINES FROM POD FROM CRONJOB {}".format(self.config["name"]))
                for line in logs.iter_lines():
                    line = line.decode('utf-8')
                    for index in range(0,len(self.config["contexts"])):
                        try:
                            regex_sub = self.REGEX_TEMPLATE_CAPT_METRCIS.format(self.config["contexts"][index]["name"],self.config["contexts"][index]["regex_sub"])
                            if re.search(regex_sub,str(line)) is not None:
                                line = re.sub(regex_sub,"",str(line))
                                line = json.loads(line)
                                validateStruct({"times_write":{},"times_read":{}},line)
                                threads[index] = [
                                    Thread(target=self.consolidTimeRead,args=[self.config["contexts"][index],line]),
                                    Thread(target=self.consolidTimeWrite,args=[self.config["contexts"][index],line])
                                ]
                                
                                threads[index][0].start()
                                threads[index][1].start()

                        except (json.JSONDecodeError,StructValidateException):
                            continue
                    while (not not len(threads)):
                        for index in list(threads):
                            if not threads[index][0].is_alive() and not threads[index][1].is_alive():
                                threads.pop(index)
            except (req.RequestException,json.JSONDecodeError,StructValidateException,ForceSleep):
                pass
            for timer_type in self.metrics:
                for capture in self.metrics[timer_type]:
                    self.metrics[timer_type][capture]["cur"].set(0)
            
            sleep(self.TIME_BETWEEN_ITERS)

    def getMetrics(self):
        return registry_to_text(self.registry)

    def __setattr__(self, name, value):
        pass

class ForceSleep(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)