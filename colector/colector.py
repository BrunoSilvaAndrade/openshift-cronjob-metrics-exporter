import logging
import json
import requests as req

from utils.struct_validate import validateStructColectors,StructColectorsException
from threading import Thread
from .exceptions import ColectorInitError

class Colector(object):

    def __init__(self,*args,**kwargs):
        try:
            validateStructColectors(kwargs)
        except StructColectorsException:
            raise ColectorInitError("ERROR INIT COLECTOR, WRONG DICT ARGS: %s"%(json.dumps(kwargs)))

        self.__dict__["context"] = kwargs

    def __setattr__(self, name, value):
        pass