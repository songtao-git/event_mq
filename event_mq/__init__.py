# coding: utf-8
from event_mq import event, mq_server, settings, registry

# register mq_servers
for name, data in settings.get('MQ_SERVERS').items():
    server = mq_server.MqServer(data['url'], data['exchange'],
                                data.get('reconnect_delay', 5),
                                registry.io_loop())
    server.start()
    registry.Registry._add_mq_server(name, server)
