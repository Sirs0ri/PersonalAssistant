import logging

import queues

# TODO: Add Updater

LOGGER = logging.getLogger(__name__)
INITIALIZED = False

LOGGER.debug("I was imported.")


def _init():
    LOGGER.info("Initializing...")
    return True


def stop():
    LOGGER.info("Exiting...")
    queues.stop()
    return True


def initialize():
    global INITIALIZED
    if not INITIALIZED:
        INITIALIZED = _init()
