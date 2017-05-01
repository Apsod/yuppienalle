from autobahn.asyncio.websocket import WebSocketServerProtocol, WebSocketServerFactory
import asyncio
import logging
import json
import numpy
import itertools
from .game import GameState, row_norms

INF = float('inf')

async def game(factory):
    dt = 1 / 20
    gamestate = GameState(500, 500, len(factory.clients), 40)
    client2index = {client: index for index, client in zip(itertools.count(), factory.clients.keys())}
    index2client = client2index.keys()
    #straight = range(0,10)
    #rot = range(10, 20)
    while(1):
        gamestate.turn([index for client, index in client2index.items() if factory.clients[client] == b'left'], -20, dt)
        gamestate.turn([index for client, index in client2index.items() if factory.clients[client] == b'right'], 20, dt)
        gamestate.straight([index for client, index in client2index.items() if factory.clients[client] == b'straight'], dt)

        gamestate.wrap()
        if factory.screen:
            factory.push_screen(json.dumps(gamestate.positions.tolist()).encode('utf8'))
        else:
            break
        await asyncio.sleep(dt)

class Factory(WebSocketServerFactory):
    def __init__(self, *args, **kwargs):
        super(Factory, self).__init__(*args, **kwargs)
        self.clients = {}
        self.screen = None

    def register_controller(self, client):
        self.clients[client] = ''

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
        self.clients[service] = payload

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
    addr = '127.0.0.1'
    coro = loop.create_server(factory, addr, 9000)
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
