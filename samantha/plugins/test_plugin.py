"""A plugin to test loading plugins. It doesn't do anything."""

###############################################################################
#
# TODO: [ ]
#
###############################################################################


# standard library imports
import logging

# related third party imports

# application specific imports
from samantha.core import subscribe_to
from samantha.plugins.plugin import Plugin
from samantha.tools import eventbuilder


__version__ = "1.3.5"


# Initialize the logger
LOGGER = logging.getLogger(__name__)

PLUGIN = Plugin("Test", True, LOGGER, __file__)


@subscribe_to("system.onstart")
def start_func(key, data):
    """Test the 'onstart' event."""
    LOGGER.debug("I'm now doing something productive!")
    return "I'm now doing something productive!"


@subscribe_to(["test", "test.1", "test.plugin"])
def test1(key, data):
    """Test various events."""
    for i in range(50):
        eventbuilder.Event(sender_id=PLUGIN.name,
                           keyword="wait").trigger()
    LOGGER.warn("Test1 successful!\n%s - %s", key, data)
    return "Test1 successful!\n%s - %s".format(key, data)


@subscribe_to("test.2")
def test2(key, data):
    """Test the 'test.2' event."""
    LOGGER.warn("Test2 successful!\n%s - %s", key, data)
    return "Test1 successful!\n%s - %s".format(key, data)


@subscribe_to("system.onexit")
def stop_func(key, data):
    """Test the 'onexit' event."""
    LOGGER.debug("I'm not doing anything productive anymore.")
    return "I'm not doing anything productive anymore."
