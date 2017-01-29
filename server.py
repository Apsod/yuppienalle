from autobahn.asyncio.websocket import WebSocketServerProtocol, WebSocketServerFactory
import asyncio

class MyServerProtocol(WebSocketServerProtocol):
    def onConnect(self, request):
        print("Client connecting: {}".format(request.peer))

    def onOpen(self):
        if self.factory.register(self):
            print('accepted')
        else:
            print('denied')

    def onClose(self, wasClean, code, reason):
        print("Socket closed: {}".format(reason))
        self.factory.unregister(self)

    def onMessage(self, payload, isBinary):
        self.factory.push(self, payload, isBinary)


def resolve(m1, m2):
    s1 = m1.decode('utf8')
    s2 = m2.decode('utf8')
    if s1 == s2:
        return 0
    elif s1 == 'paper' and s2 == 'rock':
        return 1
    elif s1 == 'rock' and s2 == 'scissor':
        return 1
    elif s1 == 'scissor' and s2 == 'paper':
        return 1
    else:
        return -1

class MyServerFactory(WebSocketServerFactory):
    def __init__(self, *args, **kwargs):
        super(MyServerFactory, self).__init__(*args, **kwargs)
        self.clients = {}


    def register(self, client):
        if len(self.clients) < 2:
            self.clients[client] = None
            return True
        else:
            return False

    def unregister(self, client):
        del self.clients[client]

    def push(self, client, payload, isBinary):
        if client in self.clients:
            self.clients[client] = payload
        [(c1, m1), (c2, m2)] = self.clients.items()
        if m1 and m2:
            w = resolve(m1, m2)
            for c in self.clients.keys():
                self.clients[c] = None
            if w == 0:
                c1.sendMessage('tie'.encode('utf8'))
                c2.sendMessage('tie'.encode('utf8'))
            elif w == 1:
                c1.sendMessage('win'.encode('utf8'))
                c2.sendMessage('loss'.encode('utf8'))
            elif w == -1:
                c1.sendMessage('loss'.encode('utf8'))
                c2.sendMessage('win'.encode('utf8'))

def main():
    factory = MyServerFactory()
    factory.protocol = MyServerProtocol
    loop = asyncio.get_event_loop()
    coro = loop.create_server(factory, '192.168.10.209', 9000)
    server = loop.run_until_complete(coro)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.close()
        loop.close()

main()
