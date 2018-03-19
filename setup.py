#!/usr/bin/env python
import distutils
from distutils.core import setup, Extension
import os

try:
    import dill
except:
    raise ImportError('Cannot open dill - may need to be installed with pip')

setup(name = 'OptimTools',
      version = '0.91',
      description = 'Tools for code and function optimization',
      author = 'Kevin A Smith',
      author_email = 'k2smith@mit.edu',
      url = 'https://github.com/kasmith/OptimTools',
      packages = ['OptimTools'],
      requires = ['dill']
      )
