import logging

LOGGER = logging.getLogger(__name__)
INITIALIZED = False

LOGGER.debug("I was imported.")


def _init():
    LOGGER.info("Initializing...")
    # TODO Load all devices
    return True


def stop():
    global INITIALIZED
    LOGGER.info("Exiting...")
    # TODO stop devices
    INITIALIZED = False
    return True


# TODO def load_devices():

# TODO def process(keyword, params={})

def initialize():
    global INITIALIZED
    if not INITIALIZED:
        INITIALIZED = _init()
    else:
        LOGGER.info("Already initialized!")
