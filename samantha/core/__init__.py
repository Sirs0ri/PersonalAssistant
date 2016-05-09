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
    global INITIALIZED
    LOGGER.info("Exiting...")
    # TODO Stop reading the input queue
    INITIALIZED = False
    return True


def initialize():
    global INITIALIZED
    if not INITIALIZED:
        INITIALIZED = _init()
    else:
        LOGGER.info("Already initialized!")
