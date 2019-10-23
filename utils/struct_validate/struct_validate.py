from .exceptions import StructValidateException,StructColectorsException

def validateStruct(struct,config):
    if isinstance(struct,dict):
        for k in struct:
            if isinstance(struct[k],dict):
                validateStruct(struct[k],config[k])
                continue
            elif isinstance(struct[k],list):
                validateStruct(struct[k],config[k])
                continue
            config[k]
        return
    elif isinstance(struct,list):
        if not isinstance(config,list):
            raise StructValidateException()
        for i in range(0,len(config)):
            if isinstance(struct[0],dict): 
                validateStruct(struct[0],config[i])
        return
    raise StructValidateException()

def validateStructColectors(colector):
    for context in colector["contexts"]:
        timers = context["timers"]
        if not isinstance(timers,dict):
            raise StructColectorsException()
        for timer in timers:
            if not isinstance(timers[timer],list):
                raise StructColectorsException()