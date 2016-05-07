import logging

import queues

LOGGER = logging.getLogger(__name__)
INITIALIZED = False

LOGGER.debug("I was imported.")


def init():
    LOGGER.info("Initializing...")
    return True

if not INITIALIZED:
    INITIALIZED = init()
