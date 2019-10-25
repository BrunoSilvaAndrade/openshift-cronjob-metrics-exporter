import json

from .exceptions import ConfigException,ConfigStructColectorsException
from os import path
from utils.struct_validate import validateStruct,validateStructColectors,StructValidateException

class Config():
    CUR_DIR = path.dirname(path.realpath(__file__))
    DEFAULT_CONFIG_FILE = "{}/{}".format(CUR_DIR,"config.json")
    CONFIG_SCHEMA = {"openshift":{"endpoint":"str","token":"str"},"colectors":[{"name":"str","contexts":[{"name":"str","regex_sub":"str","times_write":{},"times_read":{}}]}]}
    EXAMPLE_CONFIG_SCHEMA = "CONFIG EXAMPLE SHCHEMA\n{}".format(json.dumps(CONFIG_SCHEMA,indent=4))
    
    def __init__(self):

        with open(self.DEFAULT_CONFIG_FILE,"r") as f:
            file_buff = f.read()
            f.close()

        try:
            config = json.loads(file_buff)
            validateStruct(self.CONFIG_SCHEMA,config)
            for colector in config["colectors"]:
                validateStructColectors(colector)
            self.__dict__["token"] = config["openshift"]["token"]
            self.__dict__["endpoint"] = config["openshift"]["endpoint"]
            self.__dict__["colectors"] = config["colectors"]

        except json.JSONDecodeError:
            raise ConfigException("{}\n{}".format("JSON INCORRECT SYNTAX IN CONFIG FILE",self.EXAMPLE_CONFIG_SCHEMA))
        except StructValidateException:
            raise ConfigException(self.EXAMPLE_CONFIG_SCHEMA)

    def __setattr__(self, name, value):
        pass