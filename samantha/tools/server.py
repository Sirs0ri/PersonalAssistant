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
from . import eventbuilder


__version__ = "1.5.0a4"


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
STOPPED = threading.Event()

LOGGER.debug("I was imported.")


def get_uid():
    """Provide a unique id.

    The UID is used as identifier for the different server-client-connections.
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


def stop_server():
    STOPPED.set()
    if len(INDEX) == 0:
        LOGGER.info(
            "No client connected, stopping the Server right away.")
        reactor.stop()
    else:
        for client in INDEX.values():
            client.sendClose(code=1000,
                             reason=u"Shutting down the server!")
        # TODO: Exit all connections cleanly


class UDPThread(threading.Thread):
    """Thread class with a stop() method. The thread sleeps for 'delay'
    seconds, then runs the target-function."""

    def __init__(self, *args, **kwargs):
        """Basically the original __init__(), but expanded by the delay, as
        well as a logger."""
        super(UDPThread, self).__init__(*args, **kwargs)
        self._stop_event = threading.Event()
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
            retries = 0
            while not self.stopped() and retries <= 3:

                try:
                    # Send data
                    self.logger.debug("Sending '%s'", message)
                    self.socket.sendto(message.encode("utf-8"), server_address)
                    time.sleep(5)
                    retries = 0
                except socket.error:
                    retries += 1
                    self.logger.warning(
                        "Sending the message failed. Retrying in 5 sec.")
            if retries > 3:
                self.logger.fatal("The socket couldn't establish a "
                                  "connection repeatedly.")
            elif self.stopped():
                self.logger.info("The socket was asked to shut down.")
        finally:
            self.logger.debug("Closing the socket.")
            self.socket.close()
            self.logger.debug("Exited.")

    def stop(self):
        """Stop the delay. This won't stop the thread once the target-function
        is started!"""
        self.logger.debug("Exiting...")
        self._stop_event.set()

    def stopped(self):
        """Return whether the Thread should still be running or not."""
        return self._stop_event.isSet()


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
        # add this server-client-connection to the index
        INDEX[self.uid] = self

    def onClose(self, was_clean, code, reason):
        """Handle a closed connection."""
        super(Server, self).onClose(was_clean, code, reason)
        # self.sendClose()
        LOGGER.info("[UID: %s] WebSocket connection closed: '%s'",
                    self.uid, reason)
        # remove this server-client-connection from the index
        if self.uid in INDEX:
            del INDEX[self.uid]
        if len(INDEX) == 0 and STOPPED.is_set():
            LOGGER.info(
                "[UID: %s] This was the last client, stopping the Server.",
                self.uid)
            reactor.stop()

    def onMessage(self, payload, is_binary):
        """Handle a new incoming message."""
        if is_binary:
            LOGGER.debug("[UID: %s] Binary message received: %d bytes",
                         self.uid, len(payload))
        else:
            LOGGER.debug("[UID: %s] Text message received: '%s'",
                         self.uid, payload.decode('utf8'))
            if payload.decode('utf8') == "exit_server":
                LOGGER.fatal(
                    "[UID: %s] Received the request to close the server",
                    self.uid)
                # self.sendClose(code=1000, reason=u"Shutting down the server!")
                stop_server()
            else:
                key, data = parse(payload)
                eventbuilder.eEvent(sender_id=self.uid,
                                    keyword=key,
                                    data=data).trigger()


def _wait_for_server_ip():

    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.settimeout(15)

    # Bind the socket to the port
    server_address = ('', 10000)
    LOGGER.debug('starting up on %s port %s',
                 server_address[0],
                 server_address[1])
    sock.bind(server_address)
    # expects (host, port) as arg, two brackets are on purpose
    data = None
    address = None

    try:
        LOGGER.debug('Waiting to receive message')
        # TODO: This fails in bash if the port isn't explicitly opened
        data, address = sock.recvfrom(4096)

        LOGGER.debug('received %d bytes from %s: %s', len(data), address, data)

    except socket.timeout:

        data = None
        address = None

    finally:
        sock.close()

        if data and address and data.decode("utf-8").split(":")[0] == "sam.ip.broadcast":
            ip, port = address[0], int(data.decode("utf-8").split(":")[1])
        else:
            ip, port = None, None
    return ip, port


def _init(queue_in, queue_out):
    """Initialize the module."""
    global INPUT, OUTPUT, FACTORY, UDP_THREAD

    LOGGER.info("Initializing...")
    INPUT = queue_in
    OUTPUT = queue_out

    FACTORY = WebSocketServerFactory()
    FACTORY.protocol = Server

    reactor.listenTCP(19113, FACTORY)

    LOGGER.info("Listening for remote instances of Samantha on the network.")
    remote_address = _wait_for_server_ip()
    if remote_address == (None, None):
        LOGGER.info("I'm alone on the network.")
    else:
        LOGGER.info("Remote instance found at %s:%s",
                    remote_address[0], remote_address[1])

    UDP_THREAD = UDPThread(name="udp_thread")
    UDP_THREAD.daemon = True

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
        LOGGER.warning("There is no client with the UID %s!",
                       message["sender_id"])


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
