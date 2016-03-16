# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name='widukind.py.pandaSDMX',
    version="0.1.0",
    description='pandaSDMX for Widukind',
    author='Widukind team',
    url='https://github.com/Widukind/widukind.py.pandaSDMX',
    license='AGPLv3',
    packages=find_packages(),
    include_package_data=True,
    install_requires=['pandaSDMX']
)
