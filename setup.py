# -*- coding:utf-8 -*-

import os
import sys

from setuptools import setup,find_packages

setup(
    name = '',
    version = '0.0.1',
    packages=find_packages(exclude=['bin','tests']),
    extras_require = ['jieba']
)
