import logging
import urllib3

from os import path
from utils import ExitCode
from http import HTTPStatus
from threading import Thread
from colector import Colector
from flask import Flask,Response,abort
from config import Config,ConfigException


CUR_DIR = path.dirname(path.realpath(__file__))
DEFAULT_CONFIG_FILE = "{}/{}".format(CUR_DIR,"config.json")

urllib3.disable_warnings()
logging.getLogger(__name__)
logging.basicConfig(format='[%(asctime)s][%(levelname)s][%(filename)s][%(funcName)s] * %(message)s', datefmt='%d-%b-%y %H:%M:%S',level=20)
app  = Flask(__name__)

try:
    config = Config(DEFAULT_CONFIG_FILE)
except ConfigException as e:
    logging.error(str(e))
    exit(ExitCode.FAIL)


colectors = config.colectors
threads = []
for index in range(0,len(colectors)):
    colectors[index] = Colector({**colectors[index],**config.openshift})
    threads.append(Thread(target=colectors[index].collect))
    threads[index].start()

@app.route("/<cronjob_name>/METRICS")
def get_metrics(cronjob_name):
    for colector in colectors:
        if colector.config["name"] == cronjob_name:
            resp = Response(headers={"Content-Type":"text/plain; version=0.0.4"})
            resp.data = colector.getMetrics()
            return resp
    abort(HTTPStatus.NOT_FOUND)

app.run(host='0.0.0.0')
