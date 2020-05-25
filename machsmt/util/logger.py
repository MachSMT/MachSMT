import time
from ..parser import args as settings



def log(*args,**kwargs):
    with open(settings.log_file,'a')
    for arg in args:
        try: 
            print("LOG: {}".format(arg))
        except:
            warning("Logger Failure")
    for karg in kwargs:
        try: 
            print("LOG: {}={}".format(karg,kwargs[karg]))
        except:
            warning("Logger Failure")