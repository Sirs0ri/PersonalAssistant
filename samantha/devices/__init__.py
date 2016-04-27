import logging

LOGGER = logging.getLogger(__name__)
INITIALIZED = False

LOGGER.debug("I was imported.")


def init():
    LOGGER.info("Initializing...")
    # TODO Load all devices
    return True

# TODO def load_devices():

# TODO def process(keyword, params={})

if not INITIALIZED:
    INITIALIZED = init()
