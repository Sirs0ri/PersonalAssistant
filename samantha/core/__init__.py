import logging

import tools

LOGGER = logging.getLogger(__name__)
INITIALIZED = False

LOGGER.debug("I was imported.")


def _init():
    LOGGER.info("Initializing...")
    # TODO Start reading the input queue
    return True


def stop():
    LOGGER.info("Exiting...")
    # TODO Stop reading the input queue
    return True


def initialize():
    global INITIALIZED
    if not INITIALIZED:
        INITIALIZED = _init()
