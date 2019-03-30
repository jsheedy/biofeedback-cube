#!/usr/bin/env python

from setuptools import setup, find_packages


with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='biofeedback-cube',
    version='1.0',
    description='biofeedback cube',
    author='Joseph Sheedy',
    author_email='joseph.sheedy@gmail.com',
    url='https://github.com/jsheedy/biofeedback-cube',
    install_requires=requirements,
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'cube = biofeedback_cube.cube:main'
        ]
    }
)