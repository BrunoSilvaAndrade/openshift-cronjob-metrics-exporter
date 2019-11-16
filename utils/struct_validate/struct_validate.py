from .exceptions import StructValidateException
from pprint import PrettyPrinter


INDENT_LEVEL = 4


def validateStruct(struct,config):
    try:
        if isinstance(struct,dict):
            if not isinstance(config,dict):
                raise StructValidateException()
            for k in struct:
                try:
                    if isinstance(struct[k],dict):
                        validateStruct(struct[k],config[k])
                        continue
                    elif isinstance(struct[k],list):
                        validateStruct(struct[k],config[k])
                        continue
                    elif not(isinstance(config[k],struct[k])):
                        raise StructValidateException()
                except KeyError:
                    raise StructValidateException()
            return
        elif isinstance(struct,list):
            if not isinstance(config,list):
                raise StructValidateException()
            for i in range(0,len(config)):
                if isinstance(struct[0],dict): 
                    validateStruct(struct[0],config[i])
            return
        raise StructValidateException()
    except StructValidateException:
        raise StructValidateException(PrettyPrinter(indent=INDENT_LEVEL).pformat(struct))