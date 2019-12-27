#!/usr/bin/env python3

import os

from setuptools import setup, find_packages

setup(
    name         = 'banditfuzz',
    version      = '0.1',
    description  = 'Fuzzer for SMTLIB 2.x solvers.',
    author       = 'Joe Scott, Federico Mora',
    author_email = 'joseph.scott@uwaterloo.ca, fmora@cs.toronto.edu',
    url          = 'https://github.com/j29scott/BanditFuzz',
    scripts      = [
        'bin/banditfuzz_bug',
        'bin/banditfuzz_eval',
        'bin/banditfuzz_train',
        'bin/banditfuzz_rt_rngfuzz',
        'bin/banditfuzz_rt_mutation',
        'bin/banditfuzz_bug_random',
    ],
    packages     = find_packages(),
    package_dir  = {
        'banditfuzz': 'banditfuzz',
    },
)
