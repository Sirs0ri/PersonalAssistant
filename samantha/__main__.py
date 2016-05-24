"""Samantha's main module. calling this via 'python samantha'
should start everything else"""
import logging
import Queue

from autobahn.twisted.websocket import WebSocketServerProtocol, \
                                       WebSocketServerFactory
from twisted.internet import reactor

# TODO import only what's necessary
import context
import core
import devices
import logger
import services
import tools


logger.initialize()
LOGGER = logging.getLogger(__name__)

UID = 0

def getUID():
    global UID
    UID += 1
    return UID

class Server(WebSocketServerProtocol):

    C_UID = None

    def onConnect(self, request):
        self.C_UID = getUID()
        LOGGER.info("[C_UID: %d] Client connecting: '%s'",
                    self.C_UID,
                    request.peer)

    def onOpen(self):
        LOGGER.info("[C_UID: %d] WebSocket connection open.",
                    self.C_UID)
        # self.factory.reactor.callLater(5, reactor.stop)

    def onClose(self, wasClean, code, reason):
        LOGGER.info("[C_UID: %d] WebSocket connection closed: '%s'",
                    self.C_UID,
                    reason)
        # reactor.stop()

    def onMessage(self, payload, isBinary):
        # echo back message verbatim
        if isBinary:
            LOGGER.debug("[C_UID: %d] Binary message received: %d bytes",
                         self.C_UID,
                         len(payload))
        else:
            LOGGER.debug("[C_UID: %d] Text message received: '%s'",
                         self.C_UID,
                         payload.decode('utf8'))
            if payload.decode('utf8') == "exit_server":
                LOGGER.fatal(
                    "[C_UID: %d] Received the request to close the server",
                    self.C_UID)
                self.sendClose()
                reactor.stop()
            else:
                INPUT.put({"self": self,
                           "payload": payload.decode('utf8'),
                           "isBinary": isBinary})


if __name__ == "__main__":
    LOGGER.info("Initializing...")
    LOGGER.debug("-"*47)
    LOGGER.debug("Starting Samantha")
    LOGGER.debug("-"*47)
    LOGGER.info("I'm the main handler.")

    INPUT = Queue.PriorityQueue()
    OUTPUT = Queue.PriorityQueue()

    context.initialize(INPUT, OUTPUT)
    core.initialize(INPUT, OUTPUT)
    devices.initialize(INPUT, OUTPUT)
    services.initialize(INPUT, OUTPUT)
    tools.initialize(INPUT, OUTPUT)

    LOGGER.info("Initialisation complete. Opening the Websocket")

    # TODO
    # load the context
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
