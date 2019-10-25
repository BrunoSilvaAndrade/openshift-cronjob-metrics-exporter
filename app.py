import logging
import urllib3

from threading import Thread

from utils import _ExitCode
from config import Config,ConfigException
from colector import Colector,ColectorInitError

ExitCode = _ExitCode()

try:
    config = Config()
except ConfigException as e:
    logging.error(str(e))
    exit(ExitCode.FAIL)

try:
    colectors = config.colectors
    threads = []
    for index in range(0,len(colectors)):
        colector = Colector(**{**colectors[index],"token":config.token,"endpoint":config.endpoint})
        threads.append(Thread(target=colector.start_collecotrs))
        threads[index].start()
except ColectorInitError as e:
    logging.warn(str(e))
