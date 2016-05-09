"""Samantha's main module. calling this via 'python samantha'
should start everything else"""
import logging

from autobahn.twisted.websocket import WebSocketServerProtocol, \
                                       WebSocketServerFactory
import Queue
from twisted.internet import reactor

import logger

# TODO import only what's necessary
import context
import core
import devices
import services
import tools

logger.initialize()
LOGGER = logging.getLogger(__name__)


class Server(WebSocketServerProtocol):

    def onConnect(self, request):
        LOGGER.info("Client connecting: %s", request.peer)

    def onOpen(self):
        LOGGER.info("WebSocket connection open.")
        # self.factory.reactor.callLater(5, reactor.stop)

    def onClose(self, wasClean, code, reason):
        LOGGER.info("WebSocket connection closed: %s", reason)
        # reactor.stop()

    def onMessage(self, payload, isBinary):
        # echo back message verbatim
        if isBinary:
            LOGGER.debug("Binary message received: %d bytes", len(payload))
        else:
            LOGGER.debug("Text message received: %s", payload.decode('utf8'))
            if payload.decode('utf8') == "exit_server":
                LOGGER.fatal("Received the request to close the server")
                self.sendClose()
                reactor.stop()
            else:
                INPUT.put({"self": self,
                           "payload": payload.decode('utf8'),
                           "isBinary": isBinary})
        # self.sendMessage(payload, isBinary)


if __name__ == "__main__":
    LOGGER.info("Initializing...")
    LOGGER.debug("-"*47)
    LOGGER.debug("Starting Samantha")
    LOGGER.debug("-"*47)
    LOGGER.info("I'm the main handler.")

    INPUT = Queue.PriorityQueue()
    OUTPUT = Queue.PriorityQueue()

    context.initialize()
    core.initialize(INPUT, OUTPUT)
    devices.initialize()
    services.initialize()
    tools.initialize()

    LOGGER.info("Initialisation complete. Opening the Websocket")

    # TODO
    # load the context
    # Start the core
    # Initialize devices and services
    # Start updater as part of tools

    factory = WebSocketServerFactory()
    factory.protocol = Server

    port = reactor.listenTCP(19113, factory)
    reactor.run()

    LOGGER.info("Exiting...")
    context.stop()
    devices.stop()
    services.stop()
    tools.stop()
    core.stop()
