import logging

import tools

LOGGER = logging.getLogger(__name__)
INITIALIZED = False

LOGGER.debug("I was imported.")


def init():
    LOGGER.info("Initializing...")
    # TODO Start reading the input queue
    return True

if not INITIALIZED:
    INITIALIZED = init()
