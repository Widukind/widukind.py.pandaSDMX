# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name='dbnomics-connector-pandasdmx.py',
    version="0.1.0",
    description='DB.nomics connector for Python using pandaSDMX',
    author='DB.nomics team',
    url='https://git.nomics.world/dbnomics/dbnomics-connector-pandasdmx.py',
    license='AGPLv3',
    packages=find_packages(),
    include_package_data=True,
    install_requires=['pandaSDMX']
)
