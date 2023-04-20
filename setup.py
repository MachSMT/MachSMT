#!/usr/bin/env python3

import os
from setuptools import setup, find_packages
setup(
    name='machsmt',
    version='1.0',
    description='An algorithm selection tool for SMT-LIB solvers',
    author='Joe Scott, Aina Niemetz, Mathias Preiner, Saeed Nejati, and Vijay Ganesh',
    author_email='joseph.scott@uwaterloo.ca',
    url='https://machsmt.github.io/',
    scripts=[
        'bin/machsmt',
    ],
    packages=find_packages(),
    package_dir={
        'machsmt': 'machsmt',
    },

)
