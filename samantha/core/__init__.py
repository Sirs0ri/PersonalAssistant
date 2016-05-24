"""Samantha's core module. Handles the processing of incoming commands

 - Reads the global INPUT queue
 - Parses the incoming messages
 - Forwards them to services and/or devices
 - puts results back into the OUTPUT queue

 - Reads the global OUTOUT queue
 - Sends outgoing messages back the the clients"""

###############################################################################
#
# TODO: [X] Retrieve NUM_WORKER/SENDER_THREADS from a config file
# TODO: [ ] worker()
# TODO: [ ]     remove "wait"-debugging
# TODO: [ ]     parse the message
# TODO: [ ]     forward it to services and/or devices
# TODO: [ ] sender()
# TODO: [X]     check where the message came from and if necessary, send the
#               result to the correct server/device/service
# TODO: [X] move Server into a standalone module
# TODO: [X] _init()
# TODO: [X]     move sender to a new server-module
#
###############################################################################


import ConfigParser
import json
import logging
import os
import threading
import time

import devices
import services
import tools


# Initialize the logger
LOGGER = logging.getLogger(__name__)

# Set constants
INITIALIZED = False

NUM_WORKER_THREADS = 1
NUM_SENDER_THREADS = 1

INPUT = None
OUTPUT = None

THREADS = []

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

        # open the message (JSON-String to a dict)
        message = json.loads(message)

        logger.debug("[UID: %s] Got the Item '%s'",
                     message["sender_id"],
                     message["keyword"])

        # just for debugging purposes, to simulate long processing
        if message["keyword"] == "wait":
            time.sleep(5)

        message["result"] = "Processed! Woohoo!"

        logger.info("[UID: %s] Processing of '%s' successful.",
                    message["sender_id"],
                    message["keyword"])

        # Close the message again (Dict to JSON)
        message = json.dumps(message)

        # Put the result back into the OUTPUT queue, the incoming comm for now
        OUTPUT.put(message)

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
            LOGGER.info("[UID: %s] Sending the result back",
                        message["sender_id"])
            if message["sender_id"][0] == "c":
                LOGGER.debug("Sending the result '%s' back to client %s",
                             message["result"], message["sender_id"])
                tools.server.INDEX[message["sender_id"]].sendMessage(
                    message["result"].encode('utf8'), False)
            elif message["sender_id"][0] == "d":
                LOGGER.debug("Sending results to devices isn't possible yet.")
            elif message["sender_id"][0] == "s":
                LOGGER.debug("Sending results to services isn't possible yet.")
            else:
                LOGGER.warn("Invalid UID: %s", message["sender_id"])
        else:
            LOGGER.info("[UID: %s] Not sending the result back since the "
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

    LOGGER.info("Initialisation complete.")
    return True


def stop():
    """Stops the module."""
    global INITIALIZED

    LOGGER.info("Exiting... This takes a few seconds, since all threads are "
                "stopped with a 2sec timeout.")

    for t in THREADS:
        LOGGER.debug("Waiting for thread '%s' to stop.", t.name)
        t.join(2)

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
