#!/usr/bin/env python3

import os

from setuptools import setup, find_packages

setup(
    name         = 'smtzilla',
    version      = '0.1',
    description  = 'An algorithm selection tool for SMT-LIB solvers',
    author       = 'Joe Scott, Aina Niemetz, Mathias Preiner, Vijay Ganesh',
    author_email = 'joseph.scott@uwaterloo.ca',
    url          = 'https://github.com/j29scott/smtzilla',
    scripts      = [
        'bin/smtzilla_build',
        'bin/smtzilla_select',
    ],
    packages     = find_packages(),
    package_dir  = {
        'smtzilla': 'smtzilla',
    },
)
