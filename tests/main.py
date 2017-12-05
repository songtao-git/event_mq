from tornado import gen

from event_mq import decorators, event, registry


@decorators.event_handler('tests.main.hello')
def hello_handler(msg):
    print('type of msg: %s'% type(msg))
    if isinstance(msg, event.DomainEvent):
        print('content of msg: %s' % event._dumps(msg))
    else:
        print('content of msg: %s \n' % msg)


async def test():
    for i in range(10):
        en = event.DomainEvent('tests.main.hello', content='message %s' % i, info='hello, world')
        res = await event.publish_async(en)
        print('send msg %s success: %s' % (i, res))
        await gen.sleep(0.5)

if __name__ == '__main__':
    registry.io_loop().call_later(1, test)
    registry.io_loop().start()
