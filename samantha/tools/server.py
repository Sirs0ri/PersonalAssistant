"""Samantha's server module.

Open a websocket on port 19113 to communicate with remote clients.
"""

###############################################################################
# pylint: disable=global-statement
#
# TODO: [ ]
#
###############################################################################


# standard library imports
import logging

# related third party imports
from autobahn.twisted.websocket import WebSocketServerProtocol, \
                                       WebSocketServerFactory
from twisted.internet import reactor

# application specific imports
# pylint: disable=import-error
import eventbuilder
# pylint: enable=import-error


__version__ = "1.2.6"


# Initialize the logger
LOGGER = logging.getLogger(__name__)

# Set constants
INITIALIZED = False

INPUT = None
OUTPUT = None

FACTORY = None

INDEX = {}

UID = 0

LOGGER.debug("I was imported.")


def get_uid():
    """Provide a unique id.

    The UID is used as identifier for the different server-client-connenctions.
    """
    global UID
    uid = "c_{0:04d}".format(UID)
    UID += 1
    return uid


class Server(WebSocketServerProtocol):
    """A websocket-server class."""

    def __init__(self):
        """Initialize the server."""
        self.uid = get_uid()
        super(Server, self).__init__()

    def onConnect(self, request):
        """Handle a new connecting client."""
        LOGGER.info("[UID: %s] Client connecting: '%s'",
                    self.uid, request.peer)

    def onOpen(self):
        """Handle a new open connection."""
        LOGGER.info("[UID: %s] WebSocket connection open.",
                    self.uid)
        # add this server-client-connenction to the index
        INDEX[self.uid] = self

    def onClose(self, wasClean, code, reason):
        """Handle a closed connection."""
        LOGGER.info("[UID: %s] WebSocket connection closed: '%s'",
                    self.uid, reason)
        # remove this server-client-connenction from the index
        if self.uid in INDEX:
            del INDEX[self.uid]

    def onMessage(self, payload, isBinary):
        """Handle a new incoming mesage."""
        if isBinary:
            LOGGER.debug("[UID: %s] Binary message received: %d bytes",
                         self.uid, len(payload))
        else:
            LOGGER.debug("[UID: %s] Text message received: '%s'",
                         self.uid, payload.decode('utf8'))
            if payload.decode('utf8') == "exit_server":
                LOGGER.fatal(
                    "[UID: %s] Received the request to close the server",
                    self.uid)
                self.sendClose()
                reactor.stop()
            else:
                event = eventbuilder.Event(
                    sender_id=self.uid,
                    keyword=payload.decode('utf8'))
                event.trigger()


def _init(queue_in, queue_out):
    """Initialize the module."""
    global INPUT, OUTPUT, FACTORY

    LOGGER.info("Initializing...")
    INPUT = queue_in
    OUTPUT = queue_out

    FACTORY = WebSocketServerFactory()
    FACTORY.protocol = Server

    reactor.listenTCP(19113, FACTORY)

    LOGGER.info("Initialisation complete.")
    return True


def run():
    """Open the Websocket."""
    LOGGER.info("Opening the Websocket.")
    reactor.run()


def send_message(message):
    """Send a message to one of the connected devices."""
    if message["sender_id"] in INDEX:
        INDEX[message["sender_id"]].sendMessage(
            message["result"].encode('utf8'), False)
    else:
        LOGGER.warn("There is no client with the ID %s!", message["sender_id"])


def stop():
    """Stop the module."""
    global INITIALIZED

    LOGGER.info("Exiting...")
    INITIALIZED = False
    LOGGER.info("Exited.")
    return True


def initialize(queue_in, queue_out):
    """Initialize the module when not yet initialized."""
    global INITIALIZED
    if not INITIALIZED:
        INITIALIZED = _init(queue_in, queue_out)
    else:
        LOGGER.info("Already initialized!")
