# coding: utf8
from concurrent.futures import ThreadPoolExecutor

from tornado import ioloop

from event_mq import settings


class Registry:
    _mq_servers = {}
    _io_loop = ioloop.IOLoop.instance()
    _executor_pool = ThreadPoolExecutor(settings.get('EXECUTOR_MAX_WORKERS'))

    @classmethod
    def _add_mq_server(cls, name, mq_server):
        cls._mq_servers[name] = mq_server


def get_mq_server(name):
    return Registry._mq_servers.get(name, None)


def io_loop():
    return Registry._io_loop


def executor_pool():
    return Registry._executor_pool
