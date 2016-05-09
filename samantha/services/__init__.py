import logging

LOGGER = logging.getLogger(__name__)
INITIALIZED = False

LOGGER.debug("I was imported.")


def _init():
    LOGGER.info("Initializing...")
    # TODO load services
    return True


def stop():
    global INITIALIZED
    LOGGER.info("Exiting...")
    # TODO stop services
    INITIALIZED = False
    return True


# TODO def load_services():

# TODO def process(keyword, params={}):

def initialize():
    global INITIALIZED
    if not INITIALIZED:
        INITIALIZED = _init()
    else:
        LOGGER.info("Already initialized!")
