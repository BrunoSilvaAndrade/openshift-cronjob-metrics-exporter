import json
import logging
try:
    from .exceptions import ConfigException,ConfigTimerException
except ImportError:
    from exceptions import ConfigException,ConfigTimerException

from os import path

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
            self.validateStructConfig(self.CONFIG_SCHEMA,config)
            self.validateStructConfigTimers(config)
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
        except ConfigException:
            logging.error(self.EXAMPLE_CONFIG_SCHEMA)
            raise ConfigException()
            

    def validateStructConfig(self,struct,config):
        if isinstance(struct,dict):
            for k in struct:
                if isinstance(struct[k],dict):
                    self.validateStructConfig(struct[k],config[k])
                    continue
                elif isinstance(struct[k],list):
                    self.validateStructConfig(struct[k],config[k])
                    continue
                config[k]
        elif isinstance(struct,list):
            if not isinstance(config,list):
                raise ConfigException()
            for i in range(0,len(config)):
                if isinstance(struct[0],dict): 
                    self.validateStructConfig(struct[0],config[i])

    def validateStructConfigTimers(self,config):
        for colector in config["colectors"]:
             for context in colector["contexts"]:
                timers = context["timers"]
                if not isinstance(timers,dict):
                    raise ConfigException()
                for timer in timers:
                    if not isinstance(timers[timer],list):
                        raise ConfigTimerException()

if __name__ == "__main__":
    config = Config()