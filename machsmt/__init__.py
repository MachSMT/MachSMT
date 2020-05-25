from .machsmt import MachSMT
import random,numpy
from .parser import args as settings
random.seed(settings.rng)
numpy.random.seed(settings.rng)