#!/usr/bin/python

import sys
from cx_Freeze import setup, Executable

base = None
if sys.platform == 'win32':
    base = 'Win32GUI'

executables = [
    Executable('C:/Users/arntraud/Documents/python/cluster_series.py', base=base)
]

setup(name='ClusterSeries',
      version='0.1',
      description='Cluster Series',
      executables=executables
      )

