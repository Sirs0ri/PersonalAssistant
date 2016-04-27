import logging

import tools

LOGGER = logging.getLogger(__name__)
INITIALIZED = False

LOGGER.debug("I was imported.")


def init():
    LOGGER.info("Initializing...")
    # TODO: Open websocket on port 19113
    # TODO Start the "Analyzer" that checks the context for rules
    return True

if not INITIALIZED:
    INITIALIZED = init()
