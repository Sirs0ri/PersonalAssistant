"""Samantha's core module. Handles the processing of incoming commands

 - Reads the global INPUT queue
 - Parses the incoming messages
 - Forwards them to services and/or devices
 - puts results back into the OUTPUT queue

 - Reads the global OUTOUT queue
 - Sends outgoing messages back the the clients"""

###############################################################################
#
# TODO: [ ] Retrieve NUM_WORKER/SENDER_THREADS from a config file
# TODO: [ ] worker()
# TODO: [ ]     remove "wait"-debugging
# TODO: [ ]     parse the message
# TODO: [ ]     forward it to services and/or devices
# TODO: [ ] sender()
# TODO: [ ]     move to a new server-module
# TODO: [ ]     check if the message cam from an external source, don't do
#               anything if not (e.g. if the original trigger came via plugin)
# TODO: [ ] _init()
# TODO: [ ]     move senderto a new server-module
#
###############################################################################


import logging
import threading
import time

import tools


# Initialize the logger
LOGGER = logging.getLogger(__name__)

# Set constants
INITIALIZED = False

NUM_WORKER_THREADS = 2
NUM_SENDER_THREADS = 2

INPUT = None
OUTPUT = None

LOGGER.debug("I was imported.")


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

        logger.debug("[C_UID: %d] Got the Item '%s'",
                     message["self"].C_UID,
                     message["payload"])

        # just for debugging purposes, to simulate long processing
        if message["payload"] == "wait":
            time.sleep(5)

        # Put the result back into the OUTPUT queue, the incoming commfor now
        OUTPUT.put(message)

        logger.info("[C_UID: %d] Processing of '%s' successful.",
                    message["self"].C_UID,
                    message["payload"])

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

        logger.debug("[C_UID: %d] Got the Item '%s'",
                     message["self"].C_UID,
                     message["payload"])

        # Send the result back to the client it came from
        message["self"].sendMessage(message["payload"].encode('utf8'), False)

        logger.info("[C_UID: %d] Processing of '%s' completed.",
                    message["self"].C_UID,
                    message["payload"])

        # Let the queue know that processing is complete
        OUTPUT.task_done()


def _init(InputQueue, OutputQueue):
    """Initializes the module."""
    global INPUT, OUTPUT
    LOGGER.info("Initializing...")
    INPUT = InputQueue
    OUTPUT = OutputQueue

    # Start the worker threads to process commands
    LOGGER.debug("Starting Worker")
    for i in range(NUM_WORKER_THREADS):
        t = threading.Thread(target=worker, name="worker%d" % i)
        t.daemon = True
        t.start()

    # Start the sender threads to process results
    LOGGER.debug("Starting Sender")
    for i in range(NUM_SENDER_THREADS):
        t = threading.Thread(target=sender, name="sender%d" % i)
        t.daemon = True
        t.start()

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
