import re
import json
import logging
import requests as req

from .constats import *
from .exceptions import *

from time import sleep
from threading import Thread
from datetime import datetime
from schema import Schema,And,Use,SchemaError

from pyprometheus import Gauge,Counter
from pyprometheus import LocalMemoryStorage
from pyprometheus.registry import BaseRegistry
from pyprometheus.utils.exposition import registry_to_text

class Colector(object):

    def __init__(self,config):

        self.config = config
        self.metrics = {"Gauge":{},"Counter":{}}
        self.registry = BaseRegistry(storage=LocalMemoryStorage())
        self.status = {
                "running":[0,Gauge("process_is_running","Process (running/not running) status.If 0 not running, if 1 running",registry=self.registry)],
                "timeRunning":[0,Gauge("time_the_process_is_running","time the process is running in ms",registry=self.registry)],
                "locked":[0,Gauge("process_is_locked","Process (locked/unlocked) status.If 0 not locked, if 1 locked",registry=self.registry)],
                "lastStatus":[0,Gauge("process_last_exec_with_error","If 0 Last execution was successful, if 1 Last exection terminate wiht Error",registry=self.registry)]
                }

        self.lastCapture = datetime.now().timestamp()

        self.HEADERS = {"Accept": "application/json","Authorization":"Bearer {}".format(self.config["token"])}

        logging.getLogger(__name__)

    def abstractMetric(self,metricClass,metricName,dataMetrics):
        metricKey = metricClass.__name__
        if metricName in dataMetrics and (isinstance(dataMetrics[metricName],int) or isinstance(dataMetrics[metricName],float)):
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

    def abstractGetStatus(self,statusName):
        return not not self.status[statusName][0]

    def setProccessState(self,**kw):
        if not set(kw).issubset(self.status):
            diff = self.status.difference(kw)
            raise TypeError("Unknown keyword arguments %r" % list(diff))
        for statusName in kw:
            kw[statusName] = int(kw[statusName])
            self.status[statusName][0] = kw[statusName]
            self.status[statusName][1].set(kw[statusName])
    
    def proccessIsRunning(self):
        return self.abstractGetStatus("running")

    def proccessIsLocked(self):
        return self.abstractGetStatus("locked")

    def getLastStatus(self):
        return self.abstractGetStatus("lastStatus")

    def monitorProccessLock(self):
        while True:
            sleep(self.config["maxWaitPerRecord"]/2)
            if self.proccessIsRunning():
                self.setProccessState(locked=self.lastCapture+self.config["maxWaitPerRecord"]<=datetime.now().timestamp())
                self.setProccessState(
                    timeRunning=datetime.now().timestamp()-datetime.strptime(self.curPod["status"]["containerStatuses"][0]["state"]["running"]["startedAt"],POD_FORMAT_STRPTIME).timestamp()
                )
                continue
            self.setProccessState(locked=False)

    def unregisterMetrics(self):
        self.registry = BaseRegistry(storage=LocalMemoryStorage())
        self.status["running"][1].add_to_registry(self.registry)
        self.status["locked"][1].add_to_registry(self.registry)
        self.status["lastStatus"][1].add_to_registry(self.registry)

        self.setProccessState(locked=self.proccessIsLocked())
        self.setProccessState(lastStatus=self.getLastStatus())

        for metricKey in list(self.metrics):
            for collectorKey in list(self.metrics[metricKey]):
                self.metrics[metricKey].pop(collectorKey)


    def collect(self):
        Thread(target=self.monitorProccessLock).start()
        threads = {}
        while True:
            try:
                pods = json.loads(req.get("{}/{}".format(self.config["endpoint"],API_PREFIX_GET_PODS.format(self.config["namespace"])),headers=self.HEADERS,verify=False).content)
                Schema({"items":[{"metadata":dict,"spec":dict,"status":dict}]},ignore_extra_keys=True).validate(pods)
                for self.curPod in pods["items"]:
                    try:
                        if self.curPod["metadata"]["labels"]["parent"] == CONTJOB_TEMPLATE.format(self.config["name"]) and self.curPod["status"]["phase"] == "Running":
                            break
                        self.curPod = None
                    except KeyError:
                        self.curPod = None
                if self.curPod is None:
                    logging.info("WAITING FOR POD FROM CRONJOB {}".format(self.config["name"]))
                    raise NoPodsFoundedException()
                pods = None

                logging.info("POD FROM CRONJOB {} FOUNDED".format(self.config["name"]))

                self.setProccessState(running=True)

                logs = req.get("{}/{}/{}".format(
                                    self.config["endpoint"],
                                    API_PREFIX_GET_PODS.format(self.config["namespace"]),
                                    API_POSTFIX_GET_LOGS.format(self.curPod["metadata"]["name"])),
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

                self.curPod = json.loads(req.get("{}/{}".format(self.config["endpoint"],API_PREFIX_GET_ESPECIFIED_POD.format(self.config["namespace"],self.curPod["metadata"]["name"])),headers=self.HEADERS,verify=False).content)
                Schema({"status":{"phase":And(Use(str))}},ignore_extra_keys=True).validate(self.curPod)
                if self.curPod["status"]["phase"] == "Running":
                    continue
                
                self.setProccessState(lastStatus=self.curPod["status"]["phase"] != "Succeeded")
                
            except (req.RequestException,json.JSONDecodeError,SchemaError,NoPodsFoundedException) as e:
                logging.warn("EXCEPTION INTO BASE PROCCESS FLUX -> {} {}".format(e.__class__.__name__,str(e)))
            
            self.unregisterMetrics()
            self.setProccessState(running=False)
            sleep(TIME_BETWEEN_ITERS)

    def getMetrics(self):
        return registry_to_text(self.registry)