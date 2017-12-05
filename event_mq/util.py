import datetime
import inspect

from tornado import gen
from tornado.platform.asyncio import to_tornado_future

from event_mq import datetime_help, registry


def cls_str_of_meth(meth):
    mod = inspect.getmodule(meth)
    cls = meth.__qualname__.split('.<locals>', 1)[0].rsplit('.', 1)[0]
    return '{0}.{1}'.format(mod.__name__, cls)


def cls_str_of_obj(obj):
    return '{0}.{1}'.format(obj.__class__.__module__, obj.__class__.__name__)


def cls_str_of_cls(cls):
    return '{0}.{1}'.format(cls.__module__, cls.__name__)


def meth_str(meth):
    return '{0}.{1}'.format(meth.__module__, meth.__qualname__)


def pre_serialize(data):
    if isinstance(data, list):
        data = [pre_serialize(item) for item in data]

    if isinstance(data, dict):
        for key, value in data.items():
            data[key] = pre_serialize(value)

    if isinstance(data, datetime.datetime):
        data = datetime_help.get_time_str(data)

    if isinstance(data, datetime.date):
        data = datetime_help.get_date_str(data)

    return data


def pre_deserialize(data):
    if isinstance(data, list):
        data = [pre_deserialize(item) for item in data]

    if isinstance(data, dict):
        for key, value in data.items():
            data[key] = pre_deserialize(value)
    if isinstance(data, str):
        value = datetime_help.parse_datetime(data)
        if not value:
            value = datetime_help.parse_date(data)

        data = value or data

    return data


def run_async(func, *args, **kwargs):
    if not inspect.iscoroutinefunction(func) and not gen.is_coroutine_function(func):
        fu = registry.executor_pool().submit(func, *args, **kwargs)
        fu = to_tornado_future(fu)
    else:
        fu = func(*args, **kwargs)
    return gen.convert_yielded(fu)


def import_from_str(cls_path):
    module_name, class_name = cls_path.rsplit('.', 1)
    module_meta = __import__(module_name, globals(), locals(), [class_name])
    class_meta = getattr(module_meta, class_name)
    return class_meta
