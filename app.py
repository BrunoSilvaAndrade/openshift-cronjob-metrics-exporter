import logging
import urllib3

from threading import Thread
from utils import _ExitCode
from config import Config,ConfigException
from colector import Colector,ColectorInitError
from flask import Flask,Response,abort
from http import HTTPStatus

urllib3.disable_warnings()
logging.getLogger(__name__)
logging.basicConfig(format='[%(asctime)s][%(levelname)s][%(filename)s][%(funcName)s] * %(message)s', datefmt='%d-%b-%y %H:%M:%S',level=20)
ExitCode = _ExitCode()
app  = Flask(__name__)

try:
    config = Config()
except ConfigException as e:
    logging.error(str(e))
    exit(ExitCode.FAIL)


colectors = config.colectors
threads = []
for index in range(0,len(colectors)):
    colectors[index] = Colector(**{**colectors[index],"token":config.token,"endpoint":config.endpoint})
    threads.append(Thread(target=colectors[index].collect))
    threads[index].start()

@app.route("/<sync_name>/METRICS")
def get_metrics(sync_name):
    for colector in colectors:
        if colector.config["name"] == sync_name:
            resp = Response(headers={"Content-Type":"text/plain; version=0.0.4"})
            resp.data = colector.getMetrics()
            return resp
    abort(HTTPStatus.NOT_FOUND)

app.run(host='0.0.0.0')