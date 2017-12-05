# coding: utf-8
from functools import wraps

from event_mq import event


def event_handler(event_name, mq_server='default'):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        event.subscribe(event_name, func, mq_server)
        return wrapper

    return decorator
