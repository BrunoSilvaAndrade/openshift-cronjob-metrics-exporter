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
    mod_timers = ["times_write","times_read"]
    try:
        if not isinstance(colector["contexts"],list):
            raise StructColectorsException()
        for context in colector["contexts"]:
            for mod_timer in mod_timers:
                if not (isinstance(context[mod_timer],dict)):
                    raise StructColectorsException()
                for timer in context[mod_timer]:
                    if not isinstance(context[mod_timer][timer],list):
                        raise StructColectorsException()
    except KeyError:
        raise StructColectorsException()