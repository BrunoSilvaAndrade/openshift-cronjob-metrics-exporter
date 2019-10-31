import logging
import json
import requests as req
import urllib3
import re

from utils.struct_validate import *
from threading import Thread
from .exceptions import *
from time import sleep

class Colector(object):
    TEMPLATE_VALIDATION_RESPONSE={"items":[{"metadata":{},"spec":{},"status":{}}]}
    CONTJOB_TEMPLATE = "cronjob-{}"
    TIME_BETWEEN_ITERS = 5
    API_PREFIX_GET_PODS = "api/v1/namespaces/viamais-sync/pods"
    API_POSTFIX_GET_LOGS = "{}/log?tailLines=0&follow=true"
    HEADERS={"Accept": "application/json","Authorization":"Bearer {}"}
    REGEX_TEMPLATE_CAPT_METRCIS = "^.*{} METRICS: {}:"
    METRIC_TYPES = ["avg","max","min"]
    TEMPLATE_METRIC_KEY = "{}_{}_{} {}"

    def __init__(self,*args,**kwargs):
        try:
            validateStructColectors(kwargs)
            if not(isinstance(kwargs["token"],str) == isinstance(kwargs["endpoint"],str)):
                raise ColectorInitError("ERROR INIT COLECTOR, token or endpoint is invalid!")
        except StructColectorsException:
            raise ColectorInitError("ERROR INIT COLECTOR, WRONG DICT ARGS: {}".format(json.dumps(kwargs)))
        except KeyError:
            raise ColectorInitError("ERROR INIT COLECTOR, token or endpoint is invalid!")

        self.__dict__["config"] = kwargs
        self.HEADERS["Authorization"] = self.HEADERS["Authorization"].format(self.config["token"])
        
        urllib3.disable_warnings()

        self.__dict__["metrics"] = {"times_write":{},"times_read":{}}

    def consolidate(self,index,context,line):
        for id_regex in context:
            for id_timer in line:
                value = line[id_timer]["executionTime"]
                if re.search(id_regex,id_timer) is not None:
                    for time_type in self.METRIC_TYPES:
                        if time_type in context[id_regex]:
                            if id_regex not in self.metrics[index]:
                                self.metrics[index][id_regex] = {"avg":{"sum":1,"count":1},"min":None,"max":0}
                            if time_type == "avg":
                                if value > 0:
                                    self.metrics[index][id_regex]["avg"]["sum"] += value
                                    self.metrics[index][id_regex]["avg"]["count"] += 1
                            if time_type == "max":
                                if self.metrics[index][id_regex]["max"] < value:
                                    self.metrics[index][id_regex]["max"] = value
                            if time_type == "min":
                                if self.metrics[index][id_regex]["min"] is None or self.metrics[index][id_regex]["min"] > value:
                                    self.metrics[index][id_regex]["min"] = value

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
                validateStruct(self.TEMPLATE_VALIDATION_RESPONSE,pods)
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
                    logging.warn("NO POD FROM CRONJOB {} Running".format(self.config["name"]))
                    raise StructValidateException()
                logs = req.get(
                                "{}/{}/{}".format(
                                    self.config["endpoint"],
                                    self.API_PREFIX_GET_PODS,
                                    self.API_POSTFIX_GET_LOGS.format(pod["metadata"]["name"])),
                                    headers=self.HEADERS,verify=False,stream=True)

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
            except (req.RequestException,json.JSONDecodeError,StructValidateException):
                pass
            self.__dict__["metrics"] = {"times_write":{},"times_read":{}}
            sleep(self.TIME_BETWEEN_ITERS)

    def getMetrics(self):
        ret  = ""
        for timer_type in self.metrics:
            for capture in self.metrics[timer_type]:
                ret += "{}\n{}\n{}\n".format(
                    self.TEMPLATE_METRIC_KEY.format(timer_type,capture,"avg",int(round(self.metrics[timer_type][capture]["avg"]["sum"]/self.metrics[timer_type][capture]["avg"]["count"]))),
                    self.TEMPLATE_METRIC_KEY.format(timer_type,capture,"max",self.metrics[timer_type][capture]["max"]),
                    self.TEMPLATE_METRIC_KEY.format(timer_type,capture,"min",self.metrics[timer_type][capture]["min"]))
        return ret

    def __setattr__(self, name, value):
        pass