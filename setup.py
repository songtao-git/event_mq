# -*- coding:utf-8 -*-
import os
import sys
from distutils.core import setup


def read(fname):
    """
    define 'read' func to read long_description from 'README.txt'
    """
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='event-mq',
    version='0.1',
    packages=['event_mq'],
    description='A Event Queue for communication between progress.',
    long_description=read('README.md'),
    url='https://github.com/songtao-git/event_mq',
    author='songtao',
    author_email='975765671@qq.com',
    license='MIT',
    keywords=['Event', 'progress communication'],
    install_requires=[
        'pika==0.11.0',
        'tornado==4.5.2',
    ],
)
