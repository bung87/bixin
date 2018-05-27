# -*- coding:utf-8 -*-

import os
import sys

from setuptools import setup, find_packages

install_requires = ["jieba_fast"]

setup(
    name='bixin',
    version='0.0.1',
    packages=find_packages(exclude=['bin', 'tests']),
    include_package_data=True,
    package_data={
        'bixin.data': ['*.pkl']
    },
    extras_require={
        'dev': ['prefixtree>=0.2.5', 'chardet>=3.0.4']
    },
    install_requires=install_requires
    # prefixtree need at least 0.2.5 if not in pypi install if from github
)
