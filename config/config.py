import json

from .exceptions import ConfigException,ConfigStructColectorsException
from os import path
from utils.struct_validate import validateStruct,StructValidateException

class Config():
    CUR_DIR = path.dirname(path.realpath(__file__))
    DEFAULT_CONFIG_FILE = "{}/{}".format(CUR_DIR,"config.json")
    CONFIG_SCHEMA = {"openshift":{"endpoint":str,"token":str,"namespace":str},"colectors":[{"name":str,"maxWaitPerRecord":int,"contexts":[{"regex_name":str,"Gauge":list,"Counter":list}]}]}
    EXAMPLE_CONFIG_SCHEMA = "FOLLOW CONFIG EXAMPLE SHCHEMA\n{}"
    
    def __init__(self):

        with open(self.DEFAULT_CONFIG_FILE,"r") as f:
            file_buff = f.read()
            f.close()

        try:
            config = json.loads(file_buff)
            validateStruct(self.CONFIG_SCHEMA,config)
            self.__dict__["openshift"] = config["openshift"]
            self.__dict__["colectors"] = config["colectors"]

        except json.JSONDecodeError:
            raise ConfigException("{}".format("JSON INCORRECT SYNTAX IN CONFIG FILE"))
        except StructValidateException as e:
            raise ConfigException(self.EXAMPLE_CONFIG_SCHEMA.format(str(e)))

    def __setattr__(self, name, value):
        pass