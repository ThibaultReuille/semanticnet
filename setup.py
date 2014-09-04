#!/usr/bin/env python

from setuptools import setup

setup(
    name='semanticnet',
    packages=['semanticnet'],
    version='0.2.0',
    description='Small python library to create semantic graphs in JSON.',
    author='Thibault Reuille',
    author_email='thibault@opendns.com',
    url="https://github.com/ThibaultReuille/semanticnet",
    install_requires=['networkx']
)
