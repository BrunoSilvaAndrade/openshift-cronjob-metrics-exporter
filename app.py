import json
import requests
import logging
import urllib3


from requests.utils import default_headers
from utils import _ExitCode
from os import path
from config import Config,ConfigException
from colector import Colector,ColectorInitError

ExitCode = _ExitCode()

try:
    config = Config()
except ConfigException as e:
    logging.error(str(e))
    exit(ExitCode.FAIL)

try:
    colector = Colector(**config.colectors[0],token=config.token,endpoint=config.endpoint)
    colector.collect(**colector.config["contexts"][0])
except ColectorInitError as e:
    logging.warn(str(e))