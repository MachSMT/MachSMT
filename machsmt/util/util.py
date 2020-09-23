import sys
from ..parser import parser
from ..parser import args as settings

def help_msg(): parser.print_help()

def warning(*args,**kwargs):
    print("[machsmt] warning:", end = ' ')
    for arg in args:
        try: 
            print(arg, end = ' ')
        except:
            warning("Failed to print in warning.")
    for karg in kwargs:
        try: 
            print("{}={}".format(karg,kwargs[karg]),end = ' ')
        except:
            warning("Failed to print in warning.")
    print()
    if settings.wall: sys.exit(1)

def die(*args,help=False,**kwargs):
    if help: help_msg()
    print("[machsmt] error:", end = ' ')
    for arg in args:
        try: 
            print(arg, end = ' ')
        except:
            warning("Failed to print in warning.")
    for karg in kwargs:
        try: 
            print("{}={}".format(karg,kwargs[karg]),end = ' ')
        except:
            warning("Failed to print in warning.")
    print()
        
    sys.exit(1)

