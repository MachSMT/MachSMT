import sys
import warnings
from ..config import config


def die(*args, help=False, **kwargs):
    print("[machsmt] error:", end=' ')
    for arg in args:
        try:
            print(arg, end=' ')
        except BaseException:
            warning("Failed to print in warning.")
    for karg in kwargs:
        try:
            print("{}={}".format(karg, kwargs[karg]), end=' ')
        except BaseException:
            warning("Failed to print in warning.")
    print()

    sys.exit(1)


def warning(*args, **kwargs):
    if config.wall:
        die(*args, **kwargs)
    print("[machsmt] warning:", end=' ')
    for arg in args:
        try:
            print(arg, end=' ')
        except BaseException:
            warning("Failed to print in warning.")
    for karg in kwargs:
        try:
            print("{}={}".format(karg, kwargs[karg]), end=' ')
        except BaseException:
            warning("Failed to print in warning.")
    print()
    if config.wall:
        sys.exit(1)
