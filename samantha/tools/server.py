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
import socket
import threading
import time

# related third party imports
from autobahn.twisted.websocket import WebSocketServerProtocol, \
                                       WebSocketServerFactory
from twisted.internet import reactor

# application specific imports
# pylint: disable=import-error
import eventbuilder
# pylint: enable=import-error


__version__ = "1.4.2"


# Initialize the logger
LOGGER = logging.getLogger(__name__)

# Set constants
INITIALIZED = False

INPUT = None
OUTPUT = None

FACTORY = None
UDP_THREAD = None

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


def parse(message):
    """Parse a message.

    Split the message into words, if a message contains '=', it's considered as
    parameter and will be put into data, otherwise it's appended to the keyword
    after a period.
    """
    message = message.decode('utf8')
    words = message.split(" ")
    keyword = ""
    data = {}
    for word in words:
        if "=" in word:
            # The word contains a parameter
            data[word.partition("=")[0]] = word.partition("=")[2]
        else:
            # The word is a keyword
            if keyword:
                keyword += "."
            keyword += word
    return keyword, data


class UDP_Thread(threading.Thread):
    """Thread class with a stop() method. The thread sleeps for 'delay'
    seconds, then runs the target-function."""

    def __init__(self, *args, **kwargs):
        """Basically the original __init__(), but expanded by the delay, as well
        as a logger."""
        super(UDP_Thread, self).__init__(*args, **kwargs)
        self._stop = threading.Event()
        self.logger = logging.getLogger(__name__ + "." + self.name)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.socket.settimeout(5)
        self.logger.debug("Initialisation complete.")

    def run(self):
        """Sleep for DELAY seconds, then run the original threading.Thread's
        run() function."""
        self.logger.debug("Started the thread.")

        server_address = ('255.255.255.255', 10000)
        message = 'sam.ip.broadcast:19113'

        try:
            while not self.stopped():

                # Send data
                self.logger.debug("Sending '%s'", message)
                self.socket.sendto(message, server_address)
                time.sleep(5)
        finally:
            self.logger.debug("Closing the socket.")
            self.socket.close()

        if self.stopped():
            self.logger.debug("Exited.")

    def stop(self):
        """Stop the delay. This won't stop the thread once the target-function
        is started!"""
        self.logger.debug("Exiting...")
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()


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
                # TODO: Exit all conections cleanly
                reactor.stop()
            else:
                key, data = parse(payload)
                eventbuilder.Event(sender_id=self.uid,
                                   keyword=key,
                                   data=data).trigger()


def _init(queue_in, queue_out):
    """Initialize the module."""
    global INPUT, OUTPUT, FACTORY, UDP_THREAD

    LOGGER.info("Initializing...")
    INPUT = queue_in
    OUTPUT = queue_out

    FACTORY = WebSocketServerFactory()
    FACTORY.protocol = Server

    reactor.listenTCP(19113, FACTORY)

    UDP_THREAD = UDP_Thread(name="udp_thread")

    LOGGER.info("Initialisation complete.")
    return True


def run():
    """Open the Websocket."""
    LOGGER.info("Opening the Websocket.")
    UDP_THREAD.start()
    reactor.run()


def send_message(message):
    """Send a message to one of the connected clients."""
    if message["sender_id"] in INDEX:
        INDEX[message["sender_id"]].sendMessage(
            message["result"].encode('utf8'), False)
    else:
        LOGGER.warn("There is no client with the UID %s!", message["sender_id"])


def stop():
    """Stop the module."""
    global INITIALIZED

    LOGGER.info("Exiting...")
    UDP_THREAD.stop()
    UDP_THREAD.join()
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
