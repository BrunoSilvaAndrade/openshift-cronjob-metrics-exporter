import logging
import json
import requests as req
import re

from .constats import *
from .exceptions import *

from utils.struct_validate import *
from threading import Thread
from time import sleep
from datetime import datetime
from http import HTTPStatus

from pyprometheus.registry import BaseRegistry
from pyprometheus import LocalMemoryStorage
from pyprometheus.utils.exposition import registry_to_text
from pyprometheus import Gauge,Counter

class Colector(object):

    def __init__(self,*args,**kwargs):

        self.config = kwargs
        self.metrics = {"Gauge":{},"Counter":{}}
        self.registry = BaseRegistry(storage=LocalMemoryStorage())
        self.status = {
                "state":[0,Gauge("sync_is_running","Sync (running/not running) status.If 0 not running, if 1 running",registry=self.registry)],
                "locked": Gauge("sync_is_locked","Sync (locked/unlocked) status.If 0 not locked, if 1 locked",registry=self.registry),
                "lastStatus":Gauge("sync_last_exec_with_error","If 0 Last execution was successful, if 1 Last exection terminate wiht Error",registry=self.registry)
                }

        self.lastCapture = datetime.now().timestamp()

        self.HEADERS = {"Accept": "application/json","Authorization":"Bearer {}".format(self.config["token"])}

        logging.getLogger(__name__)

    def abstractMetric(self,metricClass,metricName,dataMetrics):
        metricKey = metricClass.__name__
        if metricName in dataMetrics and isinstance(dataMetrics[metricName],int):
            lastCapture = datetime.now().timestamp()
            if metricName not in self.metrics[metricKey]:
                self.metrics[metricKey][metricName] = metricClass(metricName,"Metrics type {} of key {}".format(metricKey,metricName),registry=self.registry)
            self.lastCapture = lastCapture
            return self.metrics[metricKey][metricName],dataMetrics[metricName]
        return None,None

    def gauge(self,metricList,dataMetrics):
        for metricName in metricList:
            collector,value = self.abstractMetric(Gauge,metricName,dataMetrics)
            if collector is not None:
                collector.set(value)
            

    def counter(self,metricList,dataMetrics):
        for metricName in metricList:
            collector,value = self.abstractMetric(Counter,metricName,dataMetrics)
            if collector is not None:
                collector.inc(value)

    def setSyncState(self,state):
        state = int(not not state)
        if state:
            self.status["state"][0] = state
            self.status["state"][1].set(state)
            return
        self.status["state"][0] = state
        self.status["state"][1].set(state)
    
    def syncIsRunning(self):
        return not not self.status["state"][0]

    def monitorSyncLock(self):
        while True:
            sleep(self.config["maxWaitPerRecord"]/2)
            if self.syncIsRunning():
                self.status["locked"].set(int(self.lastCapture+self.config["maxWaitPerRecord"]<=datetime.now().timestamp()))
                continue
            self.status["locked"].set(0)

    def unregisterMetrics(self):
        self.registry = BaseRegistry(storage=LocalMemoryStorage())
        self.status["state"][1].add_to_registry(self.registry)
        self.setSyncState(self.syncIsRunning())
        self.status["locked"].add_to_registry(self.registry)
        self.status["lastStatus"].add_to_registry(self.registry)
        for metricKey in list(self.metrics):
            for collectorKey in list(self.metrics[metricKey]):
                self.metrics[metricKey].pop(collectorKey)


    def collect(self):
        Thread(target=self.monitorSyncLock).start()
        threads = {}
        while True:
            try:
                pods = json.loads(req.get("{}/{}".format(self.config["endpoint"],API_PREFIX_GET_PODS),headers=self.HEADERS,verify=False).content)
                validateStruct({"items":[{"metadata":{},"spec":{},"status":{}}]},pods)
                for pod in pods["items"]:
                    try:
                        if pod["metadata"]["labels"]["parent"] == CONTJOB_TEMPLATE.format(self.config["name"]) and pod["status"]["phase"] == "Running":
                            break
                        pod = None
                    except KeyError:
                        pod = None
                if pod is None:
                    logging.info("WAITING FOR POD FROM CRONJOB {}".format(self.config["name"]))
                    raise NoPodsFounError()
                pods = None

                logging.info("POD FROM CRONJOB {} FOUNDED".format(self.config["name"]))

                self.setSyncState(1)

                logs = req.get("{}/{}/{}".format(
                                    self.config["endpoint"],
                                    API_PREFIX_GET_PODS,
                                    API_POSTFIX_GET_LOGS.format(pod["metadata"]["name"])),
                                    headers=self.HEADERS,verify=False,stream=True)

                logging.info("RECEIVING LOG LINES FROM POD FROM CRONJOB {}".format(self.config["name"]))

                for line in logs.iter_lines():
                    line = line.decode('utf-8')
                    for index in range(0,len(self.config["contexts"])):
                        try:
                            regex_sub = REGEX_TEMPLATE_CAPT_METRCIS.format(self.config["contexts"][index]["regex_name"])
                            if re.search(regex_sub,str(line)) is not None:
                                line = re.sub(regex_sub,"",str(line))
                                line = json.loads(line)
                                self.gauge(self.config["contexts"][index]["Gauge"],line)
                                self.counter(self.config["contexts"][index]["Counter"],line)

                        except (json.JSONDecodeError):
                            continue

                res = req.get("{}/{}".format(self.config["endpoint"],API_PREFIX_GET_ESPECIFIED_POD.format(pod["metadata"]["name"])),headers=self.HEADERS,verify=False)
                pod = json.loads(res.content)

                if res.status_code == HTTPStatus.OK and pod["status"]["phase"] == "Running":
                    continue
                
                self.status["lastStatus"].set(int(res.status_code == HTTPStatus.OK and pod["status"]["phase"] != "Succeeded"))
                
            except (req.RequestException,json.JSONDecodeError,StructValidateException,NoPodsFounError):
                pass
            
            self.unregisterMetrics()
            self.setSyncState(0)
            sleep(TIME_BETWEEN_ITERS)

    def getMetrics(self):
        return registry_to_text(self.registry)

class NoPodsFounError(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)