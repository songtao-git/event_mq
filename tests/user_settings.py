# coding: utf-8

SETTINGS = {
    'MQ_SERVERS': {
        'default': {
            'url': 'amqp://test:123456@rabbitmq.dev.klicen.com:5672/zeus',
            'exchange': 'zeus',
            'reconnect_delay': 5.0
        }
    },
    'EVENT_HANDLE_TIMEOUT': 10,
    'EXECUTOR_MAX_WORKERS': 20
}
