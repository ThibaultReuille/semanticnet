#!/usr/bin/env python

import os
from setuptools import setup

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='semanticnet',
    packages=['semanticnet'],
    version='0.1.0',
    description='Small python library to create semantic graphs in JSON.',
    author='Thibault Reuille',
    author_email='thibault@opendns.com',
    url="https://github.com/ThibaultReuille/semanticnet",
    install_requires=required
)
