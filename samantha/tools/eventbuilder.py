"""A tool to create events for Sam."""

###############################################################################
#
# TODO: [ ] class Event
#
###############################################################################


import logging
import json


# Initialize the logger
LOGGER = logging.getLogger(__name__)

# Set constants
INITIALIZED = False

INPUT = None
OUTPUT = None

EVENT_ID = 0

LOGGER.debug("I was imported.")


class Event(object):
    """An event for Samantha"""

    def __init__(self, sender_id, keyword, event_type="trigger", data=None):
        global EVENT_ID

        LOGGER.debug("Building new event (#%d): %s (%s) from %s",
                     EVENT_ID, event_type, keyword, sender_id)
        self.id = EVENT_ID
        EVENT_ID += 1
        self.sender_id = sender_id
        self.keyword = keyword
        if event_type in ["trigger", "request"]:
            self.event_type = event_type
        else:
            self.event_type = "trigger"
            raise ValueError("{} is an invalid type. Allowed are 'trigger' "
                             "and 'request' This Event will be handled as "
                             "'trigger'.".format(event_type))
        self.data = data
        self.result = None

    def trigger(self):
        s = json.dumps({"sender_id":  self.sender_id,
                        "keyword":    self.keyword,
                        "event_type": self.event_type,
                        "data":       self.data})
        INPUT.put(s)



def _init(InputQueue, OutputQueue):
    """Initializes the module."""
    global INPUT, OUTPUT

    LOGGER.info("Initializing...")
    INPUT = InputQueue
    OUTPUT = OutputQueue

    # onstart event?

    LOGGER.info("Initialisation complete.")
    return True


def stop():
    """Stops the module."""
    global INITIALIZED

    LOGGER.info("Exiting...")
    INITIALIZED = False

    # onexit event?

    LOGGER.info("Exited.")
    return True


def initialize(InputQueue, OutputQueue):
    """Initialize the module when not yet initialized."""
    global INITIALIZED
    if not INITIALIZED:
        INITIALIZED = _init(InputQueue, OutputQueue)
    else:
        LOGGER.info("Already initialized!")
