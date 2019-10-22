import json
import requests
import logging
import urllib3
import re


from requests.utils import default_headers
from utils import _ExitCode
from os import path
from config import Config,ConfigException

ExitCode = _ExitCode()

try:
    config = Config()
except ConfigException:
    exit(ExitCode.FAIL)

"""urllib3.disable_warnings()

headers = default_headers()
headers.update({"Accept": "application/json","Authorization":"Bearer %s"%(config["openshift"]["token"])})

for colector in config["colectors"]:

    try:
        res = requests.get("https://%s/%s"%(config["openshift"]["endpoint"],"api/v1/namespaces/viamais-sync/pods"),headers=headers,verify=False)
        res = json.loads(res.content)
        pods = res["items"]
        res = None

        for pod in pods:
            try:
                if pod["metadata"]["labels"]["parent"] == "cronjob-%s"%(colector) and pod["status"]["phase"] == "Running":
                    pod = pod["metadata"]["name"]
                    break
            except KeyError:
                continue
        if isinstance(pod,str):
            colector = config["colectors"][colector]
            res = requests.get("https://%s/%s/%s/log?tailLines=0&follow=true"%(config["openshift"]["endpoint"],"api/v1/namespaces/viamais-sync/pods",pod),headers=headers,verify=False,stream=True)
            for line in res.iter_lines():
                print(line)
    except requests.RequestException as e:
        logging.error("REQUEST ERROR : %s"%(str(e)))
        continue
    except json.JSONDecodeError:
        logging.error("DECODER JSON REPONSE ERROR")
        continue
    except KeyError:
        logging.error("GETING POD <%s> ERROR"%(colector))
        continue"""