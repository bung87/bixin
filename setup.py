# -*- coding:utf-8 -*-

from setuptools import setup, find_packages

install_requires = ["cppjieba-py"]
extras_require = {
        'dev': ['prefixtree>=0.2.5', 'chardet>=3.0.4','opencc-python-reimplemented>=0.1.3'],
        'test': ['spec>=1.4.1','nose>=1.3.7']
    }
setup(
    name='bixin',
    version='0.0.2',
    packages=find_packages(exclude=['bin', 'tests']),
    include_package_data=True,
    package_data={
        'bixin.data': ['*.pkl']
    },
    test_suite = 'tests',
    extras_require=extras_require,
    install_requires=install_requires
    # prefixtree need at least 0.2.5 if not in pypi install if from github
)
