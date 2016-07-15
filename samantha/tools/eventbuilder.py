"""A tool to create events for Sam."""

###############################################################################
# pylint: disable=global-statement
#
# TODO: [ ]
#
###############################################################################


# standard library imports
import logging

# related third party imports

# application specific imports


__version__ = "1.3.3"


# Initialize the logger
LOGGER = logging.getLogger(__name__)

# Set constants
INITIALIZED = False

INPUT = None
OUTPUT = None

FUNC_KEYWORDS = {}

EVENT_ID = 0

LOGGER.debug("I was imported.")


def _parse_keyword(keyword):
    """Parse a keyword into substrings.

    e.g.: "system.onstart" gets parsed into:
    * "system.*"
    * "*.onstart" and
    * "system.onstart".
    This allows plugins to register to wildcards, for example every message
    that begins with "system".
    """
    result = []
    words = keyword.split(".")
    for i in range(len(words)):
        for j in range(i+1, len(words)+1):
            pre = "" if i == 0 else "*."
            post = "" if j == len(words) else ".*"
            result.append(pre + ".".join(words[i:j]) + post)
    return result


class Event(object):
    """An event for Samantha.

    Each event stores information about who triggered it, what type it is and
    of course a keyword + optional data.
    """

    def __init__(self, sender_id, keyword, event_type="trigger", data=None):
        """Initialize a new event."""
        global EVENT_ID

        LOGGER.debug("Building new event (#%d): %s (%s) from %s",
                     EVENT_ID, event_type, keyword, sender_id)
        self.event_id = EVENT_ID
        EVENT_ID += 1
        self.sender_id = sender_id
        self.keyword = keyword
        self.parsed_kw_list = _parse_keyword(self.keyword)
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
        """Put the current event into the input queue."""
        kw_in_use = False
        for kw in self.parsed_kw_list:
            if kw in FUNC_KEYWORDS:
                kw_in_use = True
                break
        if kw_in_use:
            if INITIALIZED:
                INPUT.put(self)
            else:
                LOGGER.warn("This module is not initialized correctly. This "
                            "means that booting wasn't successful, or that "
                            "the Server is about to stop.")
        else:
            LOGGER.debug("Skipping event '%s' from %s because the keyword is "
                         "not in use.", self.keyword, self.sender_id)


def _init(queue_in, queue_out):
    """Initialize the module."""
    global INPUT, OUTPUT

    LOGGER.info("Initializing...")
    INPUT = queue_in
    OUTPUT = queue_out

    LOGGER.info("Initialisation complete.")
    return True


def update_keywords(func_keywords):
    """Update the global variable FUNC_KEYWORDS."""
    global FUNC_KEYWORDS
    FUNC_KEYWORDS = func_keywords


def stop():
    """Stop the module."""
    global INITIALIZED

    LOGGER.info("Exiting...")
    INITIALIZED = False

    LOGGER.info("Exited.")
    return True


def initialize(queue_in, queue_out):
    """Initialize the module when not yet initialized."""
    global INITIALIZED
    if not INITIALIZED:
        INITIALIZED = _init(queue_in, queue_out)
    else:
        LOGGER.info("Already initialized!")
