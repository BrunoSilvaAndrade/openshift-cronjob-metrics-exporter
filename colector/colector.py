import logging
import json
import requests as req
import urllib3

from utils.struct_validate import *
from threading import Thread
from .exceptions import *

class Colector(object):
    TEMPLATE_VALIDATION_RESPONSE={"items":[{"metadata":{},"spec":{},"status":{}}]}
    TIME_BETWEEN_ITERS = 60
    API_PREFIX_GET_PODS = "api/v1/namespaces/viamais-sync/pods"
    API_POSTFIX_GET_LOGS = "%s/log?tailLines=0&follow=true"
    HEADERS={"Accept": "application/json","Authorization":"Bearer %s"}
    metrics = {"max":{},"avg":{},"min":{}}

    def __init__(self,*args,**kwargs):
        try:
            validateStructColectors(kwargs)
            if not(isinstance(kwargs["token"],str) == isinstance(kwargs["endpoint"],str)):
                raise ColectorInitError("ERROR INIT COLECTOR, token or endpoint is invalid!")
        except StructColectorsException:
            raise ColectorInitError("ERROR INIT COLECTOR, WRONG DICT ARGS: %s"%(json.dumps(kwargs)))
        except KeyError:
            raise ColectorInitError("ERROR INIT COLECTOR, token or endpoint is invalid!")

        self.__dict__["context"] = kwargs
        self.HEADERS["Authorization"] = self.HEADERS["Authorization"]%(self.context["token"])
        
        urllib3.disable_warnings()

    def collect(self,**kwargs):
        context = kwargs
        try:
            pods = req.get("https://%s/%s"%(self.context["endpoint"],self.API_PREFIX_GET_PODS),headers=self.HEADERS,verify=False)
            pods = json.loads(pods.content)
            validateStruct(self.TEMPLATE_VALIDATION_RESPONSE,pods)
            for pod in pods["items"]:
                try:
                    if pod["metadata"]["labels"]["parent"] == context["name"] and pod["status"]["phase"] == "Running":
                        break
                    pod = None
                    continue
                except KeyError:
                    pod = None
                    continue
            if pod is None:
                logging.info("NO POD FROM CRONJOB <%s> Running"%(context["name"]))
        
        except req.RequestException:
            raise ColectorGetPodsError()
        except json.JSONDecodeError:
            raise ColectorGetPodsError()
        except StructValidateException:
            raise ColectorGetPodsError()


    def __setattr__(self, name, value):
        pass