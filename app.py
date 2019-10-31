import logging
import urllib3

from threading import Thread

from utils import _ExitCode
from config import Config,ConfigException
from colector import Colector,ColectorInitError
from flask import Flask,abort
from http import HTTPStatus

logging.basicConfig(format='%(asctime)s - SYNC EXPORTER - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
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
    try:
        colectors[index] = Colector(**{**colectors[index],"token":config.token,"endpoint":config.endpoint})
        threads.append(Thread(target=colectors[index].collect))
        threads[index].start()
    except ColectorInitError as e:
        colectors.pop(index)
        logging.warn(str(e))

@app.route("/<sync_name>/METRICS")
def get_metrics(sync_name):
    for colector in colectors:
        if colector.config["name"] == sync_name:
            return colector.getMetrics()
    abort(HTTPStatus.NOT_FOUND)

app.run()