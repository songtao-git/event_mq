# coding: utf-8

SETTINGS = {
    'MQ_SERVERS': {
        'default': {
            'url': 'amqp://guest:guest@127.0.0.1:5672/test',
            'exchange': 'test',
            'reconnect_delay': 5.0
        }
    },
    'EVENT_HANDLE_TIMEOUT': 10,
    'EXECUTOR_MAX_WORKERS': 20
}
