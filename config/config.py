import json

from schema import Schema,And,Use,SchemaError
from .exceptions import ConfigException,ConfigStructColectorsException

class Config():
    
    def __init__(self,filePath):
        checkSchema = Schema({
                    "openshift":
                    {
                        "endpoint":And(Use(str)),
                        "token":And(Use(str)),
                        "namespace":And(Use(str))
                    },
                    "colectors":
                    [
                        {
                            "name":And(Use(str)),
                            "maxWaitPerRecord":And(Use(int)),
                            "contexts":
                            [
                                {
                                    "regex_name":And(Use(str)),
                                    "Gauge":And([str]),
                                    "Counter":And([str])
                                }
                            ]
                        }
                    ]
                })

        with open(filePath,"r") as f:
            file_buff = f.read()
            f.close()

        try:
            config = json.loads(file_buff)
            checkSchema.validate(config)
            for key in config:
                self.__dict__[key] = config[key]
        except json.JSONDecodeError:
            raise ConfigException("{}".format("JSON INCORRECT SYNTAX IN CONFIG FILE"))
        except SchemaError as e:
            raise ConfigException(str(e))

    def __setattr__(self, name, value):
        pass