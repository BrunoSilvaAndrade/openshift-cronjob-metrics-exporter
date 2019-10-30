import logging
import urllib3

from threading import Thread

from utils import _ExitCode
from config import Config,ConfigException
from colector import Colector,ColectorInitError
from time import sleep

ExitCode = _ExitCode()

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

while True:
    for colector in colectors:
        colector.zabbixSender()
    sleep(1)