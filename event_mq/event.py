# coding: utf-8
import json
import time

from tornado import gen

from event_mq import datetime_help, util, registry


class DomainEvent:
    def __init__(self, event_name, **kwargs):
        # self.version = None
        # self.aggregator_id = None
        # self.command_id = None
        self.occur_on = datetime_help.get_utc_time()
        self.event_name = event_name
        self.__dict__.update(kwargs)


def _dumps(event):
    data = {}
    for k, v in event.__dict__.items():
        if k.startswith('__') and k.endswith('__'):
            continue
        data[k] = v
    data = util.pre_serialize(data)
    return json.dumps(data)


def _loads(data):
    data = json.loads(data)
    data = util.pre_deserialize(data)
    return DomainEvent(**data)

async def publish_async(event, mq_server='default'):
    server = registry.get_mq_server(mq_server)
    if not server:
        raise Exception('cannot find named "{0}" mq_server'.format(mq_server))
    return await server.publish_async(event.event_name, _dumps(event))


def publish(event, mq_server='default'):
    server = registry.get_mq_server(mq_server)
    if not server:
        raise Exception('cannot find named "{0}" mq_server'.format(mq_server))
    registry.io_loop().spawn_callback(server.publish_async, event.event_name, _dumps(event))


def subscribe(event_name, subscriber, mq_server='default'):
    server = registry.get_mq_server(mq_server)
    if not server:
        raise Exception('cannot find named "{0}" mq_server'.format(mq_server))
    queue = util.meth_str(subscriber)
    server.add_consumer(queue, event_name, subscriber)
