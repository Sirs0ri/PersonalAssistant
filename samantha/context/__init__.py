import logging

LOGGER = logging.getLogger(__name__)
INITIALIZED = False

LOGGER.debug("I was imported.")


def init():
    LOGGER.info("Initializing...")
    # TODO Start the context, maybe even load the last one
    # TODO Start updater
    #      Checks if properties are expired
    #      Compares Context and rules
    return True

# TODO def import_from_file(path="data/context.json"):
    # TODO Load the file as json
    # TODO Compare the property's TTLs to the current time
    #      and load only valide ones

# TODO def setProperty(property, value, ttl):

# TODO def getProperty(property):

# TODO def addRule(rule):


if not INITIALIZED:
    INITIALIZED = init()
