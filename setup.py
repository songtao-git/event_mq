# -*- coding:utf-8 -*-

from distutils.core import setup

setup(
    name='event_mq',
    version='0.1',
    packages=['event_mq'],
    description='A Event Queue for communication between progress.',
    url='https://github.com/songtao-git/event_mq',
    author='songtao',
    author_email='songtao@klicen.com',
    license='MIT',
    keywords=['Event', 'progress communication'],
    install_requires=[
        'pika==0.11.0',
        'tornado==4.5.2',
    ],
)
