#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='ArchiveScript',
    version="1",
    author='Alexandre Deneuve',
    author_email='alexandre.deneuve@wanadoo.fr',
    packages=find_packages(),
    entry_points = {
        'console_scripts':
        [
            'archivescript=ArchiveScript.script:main',
        ]
    },
    install_requires=[
        "joblib",
    ],
)
