import logging

import queues

# TODO: Add Updater

LOGGER = logging.getLogger(__name__)
INITIALIZED = False

LOGGER.debug("I was imported.")


def init():
    LOGGER.info("Initializing...")
    return True

if not INITIALIZED:
    INITIALIZED = init()
