import logging
import json
import requests as req
import urllib3
import re

from utils.struct_validate import *
from threading import Thread
from .exceptions import *

class Colector(object):
    TEMPLATE_VALIDATION_RESPONSE={"items":[{"metadata":{},"spec":{},"status":{}}]}
    TIME_BETWEEN_ITERS = 60
    API_PREFIX_GET_PODS = "api/v1/namespaces/viamais-sync/pods"
    API_POSTFIX_GET_LOGS = "%s/log?tailLines=0&follow=true"
    HEADERS={"Accept": "application/json","Authorization":"Bearer %s"}
    REGEX_TEMPLATE_CAPT_METRCIS = "^.*%s METRICS: %s:"
    METRIC_TYPES = ["avg","max","min"]

    metrics = {"times_write":{},"times_read":{}}

    def __init__(self,*args,**kwargs):
        try:
            validateStructColectors(kwargs)
            if not(isinstance(kwargs["token"],str) == isinstance(kwargs["endpoint"],str)):
                raise ColectorInitError("ERROR INIT COLECTOR, token or endpoint is invalid!")
        except StructColectorsException:
            raise ColectorInitError("ERROR INIT COLECTOR, WRONG DICT ARGS: %s"%(json.dumps(kwargs)))
        except KeyError:
            raise ColectorInitError("ERROR INIT COLECTOR, token or endpoint is invalid!")

        self.__dict__["config"] = kwargs
        self.HEADERS["Authorization"] = self.HEADERS["Authorization"]%(self.config["token"])
        
        urllib3.disable_warnings()

    def consolidate(self,index,context,line):
        for id_regex in context:
            for id_timer in line:
                value = line[id_timer]["executionTime"]
                if re.search(id_regex,id_timer) is not None:
                    for time_type in self.METRIC_TYPES:
                        if time_type in context[id_regex]:
                            if id_regex not in self.metrics[index]:
                                self.metrics[index][id_regex] = {"avg":{"sum":0,"count":0},"min":None,"max":0}
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


    def collect(self,**kwargs):
        context = kwargs
        try:
            pods = req.get("https://%s/%s"%(self.config["endpoint"],self.API_PREFIX_GET_PODS),headers=self.HEADERS,verify=False)
            pods = json.loads(pods.content)
            validateStruct(self.TEMPLATE_VALIDATION_RESPONSE,pods)
            for pod in pods["items"]:
                try:
                    if pod["metadata"]["labels"]["parent"] == self.config["name"] and pod["status"]["phase"] == "Running":
                        break
                    pod = None
                    continue
                except KeyError:
                    pod = None
                    continue
            if pod is None:
                logging.warn("NO POD FROM CRONJOB <%s> Running"%(self.config["name"]))
                return
            
            logs = req.get(
                            "https://%s/%s/%s"%(
                                self.config["endpoint"],
                                self.API_PREFIX_GET_PODS,
                                self.API_POSTFIX_GET_LOGS%(pod["metadata"]["name"]))
                            ,headers=self.HEADERS,verify=False,stream=True)

            regex_sub = self.REGEX_TEMPLATE_CAPT_METRCIS%(context["name"],context["regex_sub"])
            for line in logs.iter_lines():
                line = line.decode('utf-8')
                if re.search(regex_sub,str(line)) is not None:
                    line = re.sub(regex_sub,"",str(line))
                    line = json.loads(line)
                    self.consolidTimeRead(context,line)
                    self.consolidTimeWrite(context,line)
                    

        except req.RequestException:
            raise ColectorGetPodsError()
        except json.JSONDecodeError:
            raise ColectorGetPodsError()
        except StructValidateException:
            raise ColectorGetPodsError()
                        

    def __setattr__(self, name, value):
        pass