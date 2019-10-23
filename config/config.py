import json
import logging

from .exceptions import ConfigException,ConfigStructColectorsException
from os import path
from utils.struct_validate import validateStruct,validateStructColectors,StructValidateException

class Config():
    CUR_DIR = path.dirname(path.realpath(__file__))
    DEFAULT_CONFIG_FILE = "%s/%s"%(CUR_DIR,"config.json")
    CONFIG_SCHEMA = {"openshift":{"endpoint":"str","token":"str"},"colectors":[{"name":"str","contexts":[{"name":"str","regex_sub":"str","timers":{}}]}]}
    EXAMPLE_CONFIG_SCHEMA = "CONFIG EXAMPLE SHCHEMA\n%s"%(json.dumps(CONFIG_SCHEMA,indent=4))
    
    def __init__(self):

        with open(self.DEFAULT_CONFIG_FILE,"r") as f:
            file_buff = f.read()
            f.close()

        try:
            config = json.loads(file_buff)
            validateStruct(self.CONFIG_SCHEMA,config)
            for colector in config["colectors"]:
                validateStructColectors(colector)
            self.token = config["openshift"]["token"]
            self.endpoint = config["openshift"]["endpoint"]
            self.colectors = config["colectors"]

        except json.JSONDecodeError:
            logging.error("JSON INCORRECT SYNTAX IN CONFIG FILE")
            logging.error(self.EXAMPLE_CONFIG_SCHEMA)
            raise ConfigException()
        except KeyError:
            logging.error(self.EXAMPLE_CONFIG_SCHEMA)
            raise ConfigException()
        except IndexError:
            logging.error(self.EXAMPLE_CONFIG_SCHEMA)
            raise ConfigException()
        except StructValidateException:
            logging.error(self.EXAMPLE_CONFIG_SCHEMA)
            raise ConfigException()