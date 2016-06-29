"""A tiny websocket-client that shuts down Samantha's server."""

from autobahn.twisted.websocket import WebSocketClientProtocol, \
                                       WebSocketClientFactory
from twisted.internet import reactor


__version__ = "1.0.0"


class Interface(WebSocketClientProtocol):
    """Minimal implementation of a websocket client to shut down the server."""

    def onOpen(self):
        """Send the shutdown-command as soon as the connection is open."""
        self.sendMessage(u"exit_server".encode('utf8'))

    def onClose(self, wasClean, code, reason):
        """Stop the client after the server shut down successfully."""
        reactor.stop()


if __name__ == '__main__':

    FACTORY = WebSocketClientFactory()
    FACTORY.protocol = Interface

    reactor.connectTCP("127.0.0.1", 19113, FACTORY)
    reactor.run()
