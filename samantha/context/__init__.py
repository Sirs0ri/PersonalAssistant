"""Samantha's context module.

- Handles storing the current context
- saves/loads it when the program is ended/started.
- Repeatedly compares the context against a given set of rules to allow basic
  automation
"""

###############################################################################
# pylint: disable=global-statement
#
# TODO: [ ] finish initialize() and stop()
# TODO: [x]     Start a new context, then load the last one
# TODO: [ ]     Start context-updater
# TODO: [ ]         Checks if properties are expired
# TODO: [ ]         Compares Context and rules
# TODO: [x] finish stop()
# TODO: [x]     Store the current context as JSON
# TODO: [ ] def import_from_file(path="data/context_private.json"):
# TODO: [ ]     Load a previous context from JSON, then:
# TODO: [ ]     Compare the property's TTLs to the current time and load only
#               valide ones
# TODO: [x] def setProperty(property, value, ttl):
# TODO: [x] def getProperty(property):
# TODO: [ ] def addRule(rule):
#
###############################################################################


# standard library imports
from copy import copy
import datetime
import json
import logging
import os

# related third party imports

# application specific imports
from samantha.tools import eventbuilder

__version__ = "1.0.4"

# Initialize the logger
LOGGER = logging.getLogger(__name__)

# Set constants
INITIALIZED = False

INPUT = None
OUTPUT = None

CONTEXT = {"_": None, "_ttl": None}

LOGGER.debug("I was imported.")


def _has_children(obj):
    """Check if an object from the context has children."""
    obj = copy(obj)
    if "_" in obj:
        del obj["_"]
    if "_ttl" in obj:
        del obj["_ttl"]
    if "_default" in obj:
        del obj["_default"]
    return len(obj) > 0


def set_property(attribute, value, default=None, ttl=None):
    """Set an attribute inside the context to the given value."""
    path = attribute.split(".")
    data = CONTEXT
    current_path = ""
    new_path = False
    for step in path:
        if step:
            if current_path:
                current_path += "."
            current_path += step
            if step not in data:
                LOGGER.debug("Creating field %s", current_path)
                new_path = True
                data[step] = {"_": None, "_ttl": None}
            data = data[step]

    LOGGER.debug("Saving '%s'.", attribute)
    data["_"] = value
    data["_default"] = default
    data["_ttl"] = ttl
    if new_path:
        eventbuilder.eEvent(sender_id=__name__,
                            keyword="context.new_path.{}".format(attribute),
                            data={"attribute": attribute,
                                  "value": value,
                                  "default": default,
                                  "ttl": ttl})
    eventbuilder.eEvent(sender_id=__name__,
                        keyword="context.change.{}".format(attribute),
                        data={"attribute": attribute,
                              "value": value,
                              "default": default,
                              "ttl": ttl})


def get_value(attribute, default=None):
    """Read an attributes value from the context."""
    path = attribute.split(".")
    data = CONTEXT
    for step in path:
        if step:
            if step in data:
                data = data[step]
            else:
                LOGGER.error("Illegal path %s. The item %s wasn't found.",
                             attribute, step)
                data = None
                break
    if data:
        if data["_ttl"]:
            if data["_ttl"] < datetime.datetime.now():
                LOGGER.warn("This attribute is expired")
                return data["_default"]
        # LOGGER.debug("Returning %s.", data["_"])
        return data["_"]
    else:
        return default


def get_children(attribute, default=None):
    """Read an attributes value from the context."""
    # print "getting children for {}".format(attribute)
    path = attribute.split(".")
    data = CONTEXT
    # Follow the desired path into the context
    current_path = ""
    for step in path:
        if step:
            if step in data:
                if current_path:
                    current_path += "."
                current_path += step
                data = data[step]
            else:
                LOGGER.error("Illegal path %s. The item %s wasn't found.",
                             attribute, step)
                data = None
                break
    if data:
        results = {}
        if _has_children(data):
            for child in data:
                if child not in ["_", "_ttl", "_default"]:
                    results[child] = get_children("{}.{}".format(current_path,
                                                                 child))
        else:
            return get_value(current_path)
        # LOGGER.debug("Returning %s.", results)
        return results
    else:
        return default


def _init(queue_in, queue_out):
    """Initialize the module."""
    global INPUT, OUTPUT, CONTEXT

    LOGGER.info("Initializing...")
    INPUT = queue_in
    OUTPUT = queue_out
    try:
        this_dir = os.path.split(__file__)[0]
        with open("{}/context_private.json".format(this_dir)) as data_file:
            CONTEXT = json.load(data_file)
        LOGGER.debug("Loaded the context successfully.")
    except IOError:
        LOGGER.error("The context could not be found at %s", this_dir)

    LOGGER.info("Initialisation complete.")
    return True


def stop():
    """Stop the module."""
    global INITIALIZED

    LOGGER.info("Exiting...")
    this_dir = os.path.split(__file__)[0]
    with open("{}/context_private.json".format(this_dir), "w+") as data_file:
        json.dump(CONTEXT, data_file, sort_keys=True, indent=4)
        LOGGER.debug("Saved the context successfully.")
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
