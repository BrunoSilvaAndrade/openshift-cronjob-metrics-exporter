from .exceptions import StructValidateException
from pprint import PrettyPrinter


INDENT_LEVEL = 4


def validateStruct(structBase,structAnalyse):
    try:
        if isinstance(structBase,dict):
            if not isinstance(structAnalyse,dict):
                raise StructValidateException()
            for k in structBase:
                try:
                    if isinstance(structBase[k],dict):
                        validateStruct(structBase[k],structAnalyse[k])
                        continue
                    elif isinstance(structBase[k],list):
                        validateStruct(structBase[k],structAnalyse[k])
                        continue
                    elif not(isinstance(structAnalyse[k],structBase[k])):
                        raise StructValidateException()
                except KeyError:
                    raise StructValidateException()
            return
        elif isinstance(structBase,list):
            if not isinstance(structAnalyse,list):
                raise StructValidateException()
            for i in range(0,len(structAnalyse)):
                if isinstance(structBase[0],dict): 
                    validateStruct(structBase[0],structAnalyse[i])
            return
        raise StructValidateException()
    except StructValidateException:
        raise StructValidateException("FOLLOW THIS STRUCT FORMAT {}".format(PrettyPrinter(indent=INDENT_LEVEL).pformat(structBase)))