import logging
import threading
import time

import tools

LOGGER = logging.getLogger(__name__)
INITIALIZED = False

NUM_WORKER_THREADS = 1  # TODO: Retrieve from global config
NUM_SENDER_THREADS = 2  # TODO: Retrieve from global config

INPUT = None
OUTPUT = None

LOGGER.debug("I was imported.")


def worker():
    LOGGER = logging.getLogger(__name__ + ".worker")
    while True:
        LOGGER.info("Waiting for an item.")
        message = INPUT.get()
        LOGGER.debug("Got the Item %s", message["payload"])
        if message["payload"] == "wait":
            time.sleep(5)
        OUTPUT.put(message)
        LOGGER.debug("Added the item to the output queue.")
        INPUT.task_done()


def sender():
    LOGGER = logging.getLogger(__name__ + ".sender")
    while True:
        LOGGER.info("Waiting for an item.")
        message = OUTPUT.get()
        LOGGER.debug("Got the Item %s", message["payload"])
        message["self"].sendMessage(message["payload"].encode('utf8'), False)
        LOGGER.debug("Sent the result back.")
        OUTPUT.task_done()

def _init(InputQueue, OutputQueue):
    global INPUT
    global OUTPUT
    LOGGER.info("Initializing...")
    INPUT = InputQueue
    OUTPUT = OutputQueue

    LOGGER.info("Starting Worker")
    for i in range(NUM_WORKER_THREADS):
        t = threading.Thread(target=worker)
        t.daemon = True
        t.start()

    for i in range(NUM_SENDER_THREADS):
        t = threading.Thread(target=sender)
        t.daemon = True
        t.start()
    return True


def stop():
    global INITIALIZED
    LOGGER.info("Exiting...")
    # TODO Stop reading the input queue

    # INPUT.join()
    # OUTPUT.join()
    INITIALIZED = False
    return True


def initialize(InputQueue, OutputQueue):
    global INITIALIZED
    if not INITIALIZED:
        INITIALIZED = _init(InputQueue, OutputQueue)
    else:
        LOGGER.info("Already initialized!")
