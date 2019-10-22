import json
from os import path
import logging
import exceptions
from utils import _ExitCode

CUR_DIR = path.dirname(path.realpath(__file__))
DEFAULT_CONFIG_FILE = "%s/%s"%(CUR_DIR,"config.json")
CONFIG_SCHEMA = {"openshfit":{"endpoint":"str","token":"str",},"colectors":{"sync-example":{"context-capture-example":{"regex-line-capture-example":{"endpoint-capture-example":["avg","max","min"]}}}}}
EXAMPLE_CONFIG_SCHEMA = "CONFIG EXAMPLE SHCHEMA\n%s"%(json.dumps(CONFIG_SCHEMA,indent=4))

ExitCode = _ExitCode()
with open(DEFAULT_CONFIG_FILE,"r") as f:
    file_buff = f.read()
    f.close()

try:
    config = json.loads(file_buff)
    if not (isinstance(config["openshfit"]["token"],str) and isinstance(config["openshfit"]["endpoint"],str) and isinstance(config["colectors"],dict)):
        raise exceptions.ConfigException()
except json.JSONDecodeError:
    logging.error("JSON INCORRECT SYNTAX IN CONFIG FILE")
    logging.error(EXAMPLE_CONFIG_SCHEMA)
    exit(ExitCode.FAIL)
except KeyError:
    logging.error(EXAMPLE_CONFIG_SCHEMA)
    exit(ExitCode.FAIL)
except exceptions.ConfigException:
    logging.error(EXAMPLE_CONFIG_SCHEMA)
    exit(ExitCode.FAIL)