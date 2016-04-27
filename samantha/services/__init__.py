import logging

LOGGER = logging.getLogger(__name__)
INITIALIZED = False

LOGGER.debug("I was imported.")


def init():
    LOGGER.info("Initializing...")
    # TODO load services
    return True

# TODO def load_services():

# TODO def process(keyword, params={}):

if not INITIALIZED:
    INITIALIZED = init()
