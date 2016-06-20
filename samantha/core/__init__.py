"""Samantha's core module. Handles the processing of incoming commands

 - Reads the global INPUT queue
 - Parses the incoming messages
 - Forwards them to services and/or devices
 - puts results back into the OUTPUT queue

 - Reads the global OUTOUT queue
 - Sends outgoing messages back the the clients"""

###############################################################################
#
# TODO: [ ] worker()
# TODO: [ ]     parse the message
# TODO: [ ]     put the original Message into OUTPUT, not as JSON
#
###############################################################################


import ConfigParser
import json
import logging
import os
import threading
import time
import traceback

import devices
import services
import tools


__version__ = "1.2.2"

# Initialize the logger
LOGGER = logging.getLogger(__name__)

# Set constants
INITIALIZED = False

NUM_WORKER_THREADS = 1
NUM_SENDER_THREADS = 1

INPUT = None
OUTPUT = None

THREADS = []

KEYWORDS = {}

LOGGER.debug("I was imported.")


class Processor(object):

    def process(self, key, data=None):

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
        return False


def add_keywords(keywords):
    """Adds a set of keywords to the core's list. Based on these keywords it
    will direct commands to services and/or devices."""
    global KEYWORDS
    for key in keywords:
        if key in KEYWORDS:
            KEYWORDS[key] += keywords[key]
        else:
            KEYWORDS[key] = keywords[key]

    tools.eventbuilder.update_keywords(KEYWORDS)
    LOGGER.info("%d new keywords added to the index. It now has %d entries.",
                len(keywords), len(KEYWORDS))
    LOGGER.debug("%s", KEYWORDS.keys())


def worker():
    """Reads and processes commands from the INPUT queue. Puts results back
    into OUTPUT"""
    # Get a new logger for each thread.
    # Used instead of the global LOGGER on purpose inside this function.
    logger = logging.getLogger(
        __name__ + "." + threading.current_thread().name)

    while True:
        # Wait until an item becomes available in INPUT
        logger.debug("Waiting for an item.")
        message = INPUT.get()

        # open the message (JSON-String to a dict)
        message = json.loads(message)

        logger.debug("[UID: %s] Now processing '%s'",
                     message["sender_id"],
                     message["keyword"])

        results = [False]
        if message["keyword"] in KEYWORDS:
            for item in KEYWORDS[message["keyword"]]:
                try:
                    r = item.process(key=message["keyword"],
                                     data=message["data"])
                    results.append(r)
                except Exception as e:
                    LOGGER.exception("Exception in user code:\n%s",
                                 traceback.format_exc())
        results = [x for x in results if x]

        if results:
            message["result"] = results
            s = ""
            logger.info("[UID: %s] Processing of '%s' successful. %d result%s.",
                        message["sender_id"],
                        message["keyword"],
                        len(results),
                        ("s" if len(results) > 1 else ""))
            logger.debug("Keyword: %s Result: %s",
                         message["keyword"],
                         results)
        else:
            message["result"] = "No matching plugin/device found"
            logger.debug("[UID: %s] Processing of '%s' unsuccessful.",
                         message["sender_id"],
                         message["keyword"])

        # Put the result back into the OUTPUT queue, the incoming comm for now
        if message["event_type"] == "request":
            OUTPUT.put(json.dumps(message))

        # Let the queue know that processing is complete
        INPUT.task_done()


def sender():
    """Reads processed commands from the OUTPUT queue, then sends them back to
    to the client they came from"""
    # Get a new logger for each thread.
    # Used instead of the global LOGGER on purpose inside this function.
    logger = logging.getLogger(
        __name__ + "." + threading.current_thread().name)

    while True:
        # Wait until an item becomes available in OUTPUT
        logger.debug("Waiting for an item.")
        message = OUTPUT.get()

        # open the message (JSON-String to a dict)
        message = json.loads(message)

        logger.debug("[UID: %s] Got the Item '%s'",
                     message["sender_id"],
                     message["keyword"])

        # If the message was a request...
        if message["event_type"] == "request":
            # ...send it's result back to where it came from
            LOGGER.debug("[UID: %s] Sending the result back",
                         message["sender_id"])
            if message["sender_id"][0] == "c":
                # Original message came from a client via the server
                LOGGER.debug("Sending the result '%s' back to client %s",
                             message["result"], message["sender_id"])
                tools.server.send_message(message)
            elif message["sender_id"][0] == "d":
                # Original message came from a device
                LOGGER.debug("Sending results to devices isn't possible yet.")
            elif message["sender_id"][0] == "s":
                # Original message came from a service
                LOGGER.debug("Sending results to services isn't possible yet.")
            else:
                LOGGER.warn("Invalid UID: %s", message["sender_id"])
        else:
            LOGGER.debug("[UID: %s] Not sending the result back since the "
                         "event was a trigger.", message["sender_id"])

        logger.info("[UID: %s] Processing of '%s' completed.",
                    message["sender_id"],
                    message["keyword"])

        # Let the queue know that processing is complete
        OUTPUT.task_done()


def _init(InputQueue, OutputQueue):
    """Initializes the module."""
    global INPUT, OUTPUT, NUM_WORKER_THREADS, NUM_SENDER_THREADS, THREADS

    LOGGER.info("Initializing...")
    INPUT = InputQueue
    OUTPUT = OutputQueue

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

    NUM_WORKER_THREADS = config.getint(__name__, "NUM_WORKER_THREADS")
    NUM_SENDER_THREADS = config.getint(__name__, "NUM_SENDER_THREADS")

    # Start the worker threads to process commands
    LOGGER.debug("Starting Worker")
    for i in range(NUM_WORKER_THREADS):
        t = threading.Thread(target=worker, name="worker%d" % i)
        t.daemon = True
        t.start()
        THREADS.append(t)

    # Start the sender threads to process results
    LOGGER.debug("Starting Sender")
    for i in range(NUM_SENDER_THREADS):
        t = threading.Thread(target=sender, name="sender%d" % i)
        t.daemon = True
        t.start()
        THREADS.append(t)

    # Add the Processor-class htat handles a few commands to the keyword-index
    add_keywords({"wait": [Processor()], "logger": [Processor()]})

    LOGGER.info("Initialisation complete.")
    return True


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
