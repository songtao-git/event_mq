# coding: utf-8
import logging
import traceback

import pika
from pika import adapters
from tornado import concurrent, gen

from event_mq import util, event, registry, settings

LOGGER = logging.getLogger(__name__)


def _get_channel(connection):
    f = concurrent.Future()

    def on_open(channel):
        f.set_result(channel)

    if not connection.is_open:
        f.set_exception(Exception('connection is closed, cannot get channel'))

    connection.channel(on_open_callback=on_open)
    return f


class Consumer:
    def __init__(self, exchange, queue, routing_key, handler, io_loop=None):
        self._exchange = exchange
        self._queue = queue
        self._routing_key = routing_key
        self._handler = handler
        self.running = False
        self._connection = None
        self._io_loop = io_loop or registry.io_loop()

    def __on_message(self, channel, deliver, properties, body):
        encoding = properties.content_encoding or 'utf-8'
        body = body.decode(encoding)
        LOGGER.debug('receive message from mq: %s', body)

        try:
            data = event._loads(body)
        except:
            data = body
        try:
            def handle_ack(future):
                if future.exception():
                    channel.basic_nack(deliver.delivery_tag)
                else:
                    channel.basic_ack(deliver.delivery_tag)

            def handle_timeout(future):
                if not future.done():
                    future.set_exception(Exception('timeout'))

            fu = util.run_async(self._handler, data)
            fu.add_done_callback(handle_ack)
            self._io_loop.call_later(settings.get('EVENT_HANDLE_TIMEOUT'), handle_timeout, fu)
        except:
            LOGGER.error('handle(%s) message error: %s', self._handler, traceback.format_exc())

    async def __connect(self):
        if self._connection and self._connection.is_open and not self._connection.is_closed:
            LOGGER.debug('open channel: %s', self._queue)
            channel = await _get_channel(self._connection)
            await gen.Task(channel.queue_declare, queue=self._queue, durable=True)
            await gen.Task(channel.queue_bind, queue=self._queue, exchange=self._exchange,
                           routing_key=self._routing_key)
            channel.basic_consume(self.__on_message, self._queue)
            channel.add_on_close_callback(self._on_close)
            self.running = True

    def _on_close(self, channel, reply_code, reply_text):
        LOGGER.debug('channel(%s) closed: (%s) %s', self._queue, reply_code, reply_text)
        self.running = False
        self._io_loop.call_later(1, self.__connect)

    def start(self, connection):
        if self.running:
            return
        self._connection = connection
        self._io_loop.spawn_callback(self.__connect)


class MqServer:
    def __init__(self, url, exchange, reconnect_delay=5.0, io_loop=None):
        self._url = url
        self._exchange = exchange
        self._reconnect_delay = reconnect_delay
        self._io_loop = io_loop or registry.io_loop()
        self._connection = None
        self._closing = False
        self._consumers = set()

    def _connect(self):
        self._connection = adapters.TornadoConnection(parameters=pika.URLParameters(self._url),
                                                      on_open_callback=self.__on_connection_open,
                                                      on_open_error_callback=self.__on_connection_open_error,
                                                      on_close_callback=self.__on_connection_closed)

    def __on_connection_open(self, connection):
        self._io_loop.spawn_callback(self.__perform_connection_open)

    async def __perform_connection_open(self):
        channel = await _get_channel(self._connection)
        await gen.Task(channel.exchange_declare, exchange=self._exchange, durable=True)
        for consumer in list(self._consumers):
            consumer.start(self._connection)
        channel.close()

    def __on_connection_open_error(self, connection, error):
        if self._closing:
            return
        LOGGER.warning('Connection Open failed, reopening in %s seconds: %s',
                       self._reconnect_delay, error)

        self._connection.add_timeout(self._reconnect_delay, self._connect)

    def __on_connection_closed(self, connection, reply_code, reply_text):
        if self._closing:
            return
        LOGGER.warning('Connection Closed, reopening in %s seconds: (%s) %s',
                       self._reconnect_delay, reply_code, reply_text)

        self._connection.add_timeout(self._reconnect_delay, self._connect)

    def add_consumer(self, queue, routing_key, handler):
        consumer = Consumer(self._exchange, queue, routing_key, handler, self._io_loop)
        consumer.start(self._connection)
        self._consumers.add(consumer)
        LOGGER.debug('add consumer(queue: %s, routing_key: %s, handler: %s) to %s',
                     queue, routing_key, util.meth_str(handler), self._url)

    async def publish_async(self, routing_key, data):
        try:
            channel = await _get_channel(self._connection)
            channel.basic_publish(self._exchange, routing_key, data.encode('utf-8'))
            channel.close()
            LOGGER.debug('success publish message to (exchange: %s, routing_key: %s), and data is: %s',
                         self._exchange, routing_key, data)
            return True
        except:
            LOGGER.error('fail publish message to (exchange: %s, routing_key: %s), and data is: %s',
                         self._exchange, routing_key, data)
            return False

    def start(self):
        self._closing = False
        self._connect()

    def stop(self):
        self._closing = True
        self._connection.close()
