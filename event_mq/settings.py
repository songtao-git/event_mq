# coding: utf-8
try:
    from user_settings import SETTINGS as user_settings
except ImportError:
    user_settings = {}

DEFAULTS = {
    'MQ_SERVERS': {
        'default': {
            'url': 'amqp://guest:guest@127.0.0.1:5672',
            'exchange': '',
            'reconnect_delay': 5.0
        }
    },
    'EVENT_HANDLE_TIMEOUT': 10,
    'EXECUTOR_MAX_WORKERS': 20
}


def get(attr):
    if attr not in DEFAULTS:
        raise AttributeError("Invalid setting: '%s'" % attr)

    try:
        # Check if present in user settings
        val = user_settings[attr]
    except KeyError:
        # Fall back to defaults
        val = DEFAULTS[attr]

    return val
