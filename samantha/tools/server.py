"""Samantha's server module.

Opens a websocket on port 19113 to communicate with remote clients"""

###############################################################################
#
# TODO: [ ]
#
###############################################################################


import logging

import tools

from autobahn.twisted.websocket import WebSocketServerProtocol, \
                                       WebSocketServerFactory
from twisted.internet import reactor


# Initialize the logger
LOGGER = logging.getLogger(__name__)

# Set constants
INITIALIZED = False

INPUT = None
OUTPUT = None

factory = None

INDEX = {}

UID = 0

LOGGER.debug("I was imported.")


def get_uid():
    """provides a unique uid which is used as identifier for the different
    server-client-connenctions"""
    global UID
    uid = "c{}".format(UID)
    UID += 1
    return uid


class Server(WebSocketServerProtocol):
    """a websocket-server class"""

    def onConnect(self, request):
        self.UID = get_uid()
        LOGGER.info("[UID: %s] Client connecting: '%s'",
                    self.UID, request.peer)

    def onOpen(self):
        LOGGER.info("[UID: %s] WebSocket connection open.",
                    self.UID)
        # add this server-client-connenction to the index
        INDEX[self.UID] = self

    def onClose(self, wasClean, code, reason):
        LOGGER.info("[UID: %s] WebSocket connection closed: '%s'",
                    self.UID, reason)
        # remove this server-client-connenction from the index
        del INDEX[self.UID]

    def onMessage(self, payload, isBinary):
        if isBinary:
            LOGGER.debug("[UID: %s] Binary message received: %d bytes",
                         self.UID, len(payload))
        else:
            LOGGER.debug("[UID: %s] Text message received: '%s'",
                         self.UID, payload.decode('utf8'))
            if payload.decode('utf8') == "exit_server":
                LOGGER.fatal(
                    "[UID: %s] Received the request to close the server",
                    self.UID)
                self.sendClose()
                reactor.stop()
            else:
                e = tools.eventbuilder.Event(sender_id=self.UID,
                                             keyword=payload.decode('utf8'))
                e.trigger()


def _init(InputQueue, OutputQueue):
    """Initializes the module."""
    global INPUT, OUTPUT, factory

    LOGGER.info("Initializing...")
    INPUT = InputQueue
    OUTPUT = OutputQueue

    factory = WebSocketServerFactory()
    factory.protocol = Server

    reactor.listenTCP(19113, factory)

    LOGGER.info("Initialisation complete.")
    return True


def run():
    """open the Websocket"""
    LOGGER.info("Opening the Websocket.")
    reactor.run()


def send_message(message):
    """send a message to one of the connected devices"""
    if message["sender_id"] in INDEX:
        INDEX[message["sender_id"]].sendMessage(
            message["result"].encode('utf8'), False)
    else:
        LOGGER.warn("There is no client with the ID %s!", message["sender_id"])


def stop():
    """Stops the module."""
    global INITIALIZED

    LOGGER.info("Exiting...")
    INITIALIZED = False
    LOGGER.info("Exited.")
    return True


def initialize(InputQueue, OutputQueue):
    """Initialize the module when not yet initialized."""
    global INITIALIZED
    if not INITIALIZED:
        INITIALIZED = _init(InputQueue, OutputQueue)
    else:
        LOGGER.info("Already initialized!")
