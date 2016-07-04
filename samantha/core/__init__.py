"""Samantha's core module. Handles the processing of incoming commands.

- Reads the global INPUT queue
- Parses the incoming messages
- Forwards them to services and/or devices
- puts results back into the OUTPUT queue

- Reads the global OUTOUT queue
- Sends outgoing messages back the the clients
"""

###############################################################################
# pylint: disable=global-statement
#
#           worker()
# TODO: [ ] parse the message
# TODO: [ ] allow a hierarchy in commands,
#           Example: "media.twitch.online.channename" will trigger plugins that
#           subscribed to "media.*", "*.online.*", "media.twitch.online.*", etc
#
###############################################################################


# standard library imports
from collections import Iterable
import ConfigParser
from functools import wraps
import json
import logging
import os
import threading
import time
import traceback

# related third party imports

# application specific imports
# pylint: disable=import-error
import devices
import services
import tools
# pylint: enable=import-error


__version__ = "1.3.0"

# Initialize the logger
LOGGER = logging.getLogger(__name__)

# Set constants
INITIALIZED = False

NUM_WORKER_THREADS = 1
NUM_SENDER_THREADS = 1

INPUT = None
OUTPUT = None

KEYWORDS = {}
FUNC_KEYWORDS = {}

UID = 0

LOGGER.debug("I was imported.")


def get_uid():
    """Generate an incrementing UID for unknown plugins."""
    global UID
    uid = "u_{0:04d}".format(UID)
    UID += 1
    return uid


def subscribe_to(keyword):
    # code in this function is executed at runtime

    def decorator(func):
        # code in this function is also executed at runtime
        LOGGER.debug("Decorating '%s.%s'. Key(s): %s..", func.__module__, func.__name__, keyword)
        valid = False

        # Initialize the module
        mod = __import__(func.__module__, {}, {}, ('*', ))
        if hasattr(mod, "device"):
            if mod.device.is_active:
                if mod.device.uid == "NO_UID":
                    LOGGER.debug("This is a new device.")
                    uid = devices.get_uid()
                    mod.device.uid = uid
                else:
                    LOGGER.debug("This is an existing device.")
                valid = True
        elif hasattr(mod, "service"):
            if mod.service.is_active:
                if mod.service.uid == "NO_UID":
                    LOGGER.debug("This is a new service.")
                    uid = services.get_uid()
                    mod.service.uid = uid
                else:
                    LOGGER.debug("This is an existing service.")
                valid = True
        else:
            LOGGER.debug("This is not a valid plugin")

        if valid:
            if not isinstance(keyword, str) and isinstance(keyword, Iterable):
                for key in keyword:
                    if key not in FUNC_KEYWORDS:
                        FUNC_KEYWORDS[key] = []
                    FUNC_KEYWORDS[key].append(func)
            else:
                if keyword not in FUNC_KEYWORDS:
                    FUNC_KEYWORDS[keyword] = []
                FUNC_KEYWORDS[keyword].append(func)
                tools.eventbuilder.update_keywords(KEYWORDS, FUNC_KEYWORDS)
            LOGGER.debug("'%s.%s' decorated successfully.",
                         func.__module__,
                         func.__name__)

        @wraps(func)
        def executer(*args, **kwargs):
            # code in this function is executed once
            # the decorated function is executed
            return func(*args, **kwargs)

        return executer
    return decorator

class Subscription(object):
    def __init__(self):
        self.start = subscribe_to("onstart")
        self.event = subscribe_to
        self.exit = subscribe_to("onexit")

subscription = Subscription()

class Processor(object):
    """Replacement for a full service to handle some internal commands.

    To be removed, as soon as there is a decorator available to
    register plugins (or rather their functions in the index.)
    """

    def process(self, key, data=None):
        """Process some internal commands via the framework directly."""
        # just for debugging purposes, to simulate long processing
        if key == "wait":
            time.sleep(5)
            return True
        elif key == "logger":
            root = logging.getLogger()
            if root.handlers[2].level == 10:
                root.handlers[2].setLevel(logging.INFO)
                LOGGER.warn("Logging-Level set to INFO")
                return True
            else:
                root.handlers[2].setLevel(logging.DEBUG)
                LOGGER.warn("Logging-Level set to DEBUG")
                return True
        else:
            LOGGER.warn("Keyword not in use. (%s, %s)", key, data)
        return False


def add_keywords(keywords):
    """Add a set of keywords to the core's list.

    Based on these keywords commands are directed to services and/or devices.
    """
    for key in keywords:
        if key in KEYWORDS:
            KEYWORDS[key] += keywords[key]
        else:
            KEYWORDS[key] = keywords[key]

    tools.eventbuilder.update_keywords(KEYWORDS, FUNC_KEYWORDS)
    LOGGER.info("%d new keywords added to the index. It now has %d entries.",
                len(keywords), len(KEYWORDS))
    LOGGER.debug("%s", KEYWORDS.keys())


def worker():
    """Read and process commands from the INPUT queue.

    Puts results back into OUTPUT.
    """
    # Get a new logger for each thread.
    # Used instead of the global LOGGER on purpose inside this function.
    logger = logging.getLogger(
        __name__ + "." + threading.current_thread().name)

    while True:
        # Wait until an item becomes available in INPUT
        logger.debug("Waiting for an item.")
        event = INPUT.get()

        logger.debug("[UID: %s] Now processing '%s'",
                     event.sender_id,
                     event.keyword)

        results = [False]
        if event.keyword in KEYWORDS:
            for item in KEYWORDS[event.keyword]:
                try:
                    res = item.process(key=event.keyword,
                                       data=event.data)
                    results.append(res)
                except Exception:
                    LOGGER.exception("Exception in user code:\n%s",
                                     traceback.format_exc())
        if event.keyword in FUNC_KEYWORDS:
            for func in FUNC_KEYWORDS[event.keyword]:
                try:
                    LOGGER.warn("Executing '%s.%s'.", func.__module__, func.__name__)
                    res = func(key=event.keyword,
                               data=event.data)
                    results.append(res)
                except Exception:
                    LOGGER.exception("Exception in user code:\n%s",
                                     traceback.format_exc())
        results = [x for x in results if x]

        if results:
            event.result = results
            logger.info("[UID: %s] Processing of '%s' successful. "
                        "%d result%s.",
                        event.sender_id,
                        event.keyword,
                        len(results),
                        ("s" if len(results) > 1 else ""))
            logger.debug("Keyword: %s Result: %s",
                         event.keyword,
                         results)
        else:
            event.result = "No matching plugin/device found"
            logger.debug("[UID: %s] Processing of '%s' unsuccessful.",
                         event.sender_id,
                         event.keyword)

        # Put the result back into the OUTPUT queue, the incoming comm for now
        if event.event_type == "request":
            OUTPUT.put(event)

        # Let the queue know that processing is complete
        INPUT.task_done()


def sender():
    """Read processed commands from OUTPUT queue; send them back to client."""
    # Get a new logger for each thread.
    # Used instead of the global LOGGER on purpose inside this function.
    logger = logging.getLogger(
        __name__ + "." + threading.current_thread().name)

    while True:
        # Wait until an item becomes available in OUTPUT
        logger.debug("Waiting for an item.")
        message = OUTPUT.get()

        logger.debug("[UID: %s] Got the Item '%s'",
                     message.sender_id,
                     message.keyword)

        # If the message was a request...
        if message.event_type == "request":
            # ...send it's result back to where it came from
            LOGGER.debug("[UID: %s] Sending the result back",
                         message.sender_id)
            if message.sender_id[0] == "c":
                # Original message came from a client via the server
                LOGGER.debug("Sending the result '%s' back to client %s",
                             message.result, message.sender_id)
                tools.server.send_message(message)
            elif message.sender_id[0] == "d":
                # Original message came from a device
                LOGGER.debug("Sending results to devices isn't possible yet.")
            elif message.sender_id[0] == "s":
                # Original message came from a service
                LOGGER.debug("Sending results to services isn't possible yet.")
            else:
                LOGGER.warn("Invalid UID: %s", message.sender_id)
        else:
            LOGGER.debug("[UID: %s] Not sending the result back since the "
                         "event was a trigger.", message.sender_id)

        logger.info("[UID: %s] Processing of '%s' completed.",
                    message.sender_id,
                    message.keyword)

        # Let the queue know that processing is complete
        OUTPUT.task_done()


def _init(queue_in, queue_out):
    """Initialize the module."""
    global INPUT, OUTPUT, NUM_WORKER_THREADS, NUM_SENDER_THREADS

    LOGGER.info("Initializing...")
    INPUT = queue_in
    OUTPUT = queue_out

    # Read the number of threads to start from Samantha's config file
    # (/samantha/data/samantha.cfg)
    LOGGER.debug("Reading the config file...")
    # get the config file's path in realtion to the path of this file
    this_dir = os.path.split(__file__)[0]  # ..[1] would be the filename
    if this_dir is "":
        path = "../../data"
    else:
        path = this_dir.replace("core", "data")

    config = ConfigParser.RawConfigParser()
    config.read("{path}/samantha.cfg".format(path=path))

    try:
        NUM_WORKER_THREADS = config.getint(__name__, "NUM_WORKER_THREADS")
        NUM_SENDER_THREADS = config.getint(__name__, "NUM_SENDER_THREADS")
    except Exception:
        LOGGER.exception("Exception while reading the config:\n%s",
                         traceback.format_exc())

    # Start the worker threads to process commands
    LOGGER.debug("Starting Worker")
    for i in range(NUM_WORKER_THREADS):
        thread = threading.Thread(target=worker, name="worker%d" % i)
        thread.daemon = True
        thread.start()

    # Start the sender threads to process results
    LOGGER.debug("Starting Sender")
    for i in range(NUM_SENDER_THREADS):
        thread = threading.Thread(target=sender, name="sender%d" % i)
        thread.daemon = True
        thread.start()

    # Add the Processor-class htat handles a few commands to the keyword-index
    add_keywords({"wait": [Processor()], "logger": [Processor()]})

    LOGGER.info("Initialisation complete.")
    return True


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
