from autobahn.asyncio.websocket import WebSocketServerProtocol, WebSocketServerFactory
import asyncio
import logging
import json
import numpy



async def game(factory):
    dt = 1 / 20
    n = 4
    borders = numpy.array([500, 500])
    positions = numpy.mod(numpy.random.random((n,2)) * borders, borders)
    velocities = numpy.random.randn(n,2)*40
    while(1):
        positions = numpy.mod(positions + velocities * dt, borders)
        if factory.screen:
            factory.push_screen(json.dumps(positions.tolist()).encode('utf8'))
        else:
            break
        await asyncio.sleep(dt)

class Factory(WebSocketServerFactory):
    def __init__(self, *args, **kwargs):
        super(Factory, self).__init__(*args, **kwargs)
        self.clients = {}
        self.screen = None
        self.i = 0

    def register_controller(self, client):
        self.clients[client] = i
        self.i += 1
        return self.clients[client]

    def register_screen(self, screen):
        if self.screen is None:
            asyncio.ensure_future(game(self))
            self.screen = screen
            return True
        else:
            return False

    def unregister_controller(self, client):
        del self.clients[client]

    def unregister_screen(self, screen):
        self.screen = None

    def screen_message(self, service, payload, isBinary):
        logging.info('screen: {}'.format(payload))

    def controller_message(self, service, payload, isBinary):
        logging.info('controller: {}'.format(payload))

    def push_screen(self, msg):
        self.screen.push(msg)

class BaseService:
    def __init__(self, proto):
        self.factory = proto.factory
        self.proto = proto
        self.is_closed = False

    def onOpen(self):
        pass

    def onClose(self, wasClean, code, reason):
        pass

    def onMessage(self, payload, isBinary):
        pass


class ScreenService(BaseService):
    def onOpen(self):
        if self.factory.register_screen(self):
            logging.info('opened screen')
        else:
            logging.info('Denied, screen already connected')

    def onClose(self, wasClean, code, reason):
        self.factory.unregister_screen(self)
        logging.info('closing screen')

    def onMessage(self, payload, isBinary):
        self.factory.screen_message(self.proto, payload, isBinary)

    def push(self, msg):
        logging.info('sending to screen: {}'.format(msg))
        self.proto.sendMessage(msg, False)

class ControllerService(BaseService):
    def onOpen(self):
        self.factory.register_controller(self)

    def onClose(self, wasClean, code, reason):
        self.factory.unregister_controller(self)

    def onMessage(self, payload, isBinary):
        self.factory.controller_message(self, payload, isBinary)


class ServerProtocol(WebSocketServerProtocol):
    SERVICEMAP = {'/screen': ScreenService,
                  '/controller': ControllerService}

    def __init__(self, *args, **kwargs):
        super(ServerProtocol, self).__init__(*args, **kwargs)
        self.service = None

    def onConnect(self, request):
        # request has all the information from the initial
        # WebSocket opening handshake ..
        logging.info(request.peer)
        logging.info(request.headers)
        logging.info(request.host)
        logging.info(request.path)
        logging.info(request.params)
        logging.info(request.version)
        logging.info(request.origin)
        logging.info(request.protocols)
        logging.info(request.extensions)

        # We map to services based on path component of the URL the
        # WebSocket client requested. This is just an example. We could
        # use other information from request, such has HTTP headers,
        # WebSocket subprotocol, WebSocket origin etc etc
        ##
        if request.path in self.SERVICEMAP:
            cls = self.SERVICEMAP[request.path]
            self.type = cls.__name__
            self.service = cls(self)
            logging.info('connecting: {}'.format(self.type))
        else:
            err = "No service under %s" % request.path
            logging.info(err)
            raise ConnectionDeny(404, unicode(err))

    def onOpen(self):
        if self.service:
            self.service.onOpen()

    def onMessage(self, payload, isBinary):
        if self.service:
            self.service.onMessage(payload, isBinary)

    def onClose(self, wasClean, code, reason):
        if self.service:
            self.service.onClose(wasClean, code, reason)


def serve():
    factory = Factory()
    factory.protocol = ServerProtocol
    loop = asyncio.get_event_loop()
    coro = loop.create_server(factory, '192.168.10.210', 9000)
    server = loop.run_until_complete(coro)
    try:
        logging.info('server running')
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.close()
        loop.close()

def run():
    logging.basicConfig(level=logging.DEBUG)
    serve()

run()
