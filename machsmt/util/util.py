import sys
import warnings
from ..config import args


def die(err_msg):
    print(f"[machsmt] error: {err_msg}")
    sys.exit(1)

def warning(err_msg):
    print(f"[machsmt] warning: {err_msg}")
    if args.wall:
        sys.exit(1)
