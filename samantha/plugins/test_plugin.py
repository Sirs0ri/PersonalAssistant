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
# pylint: disable=import-error
from core import subscribe_to
from plugins.plugin import Plugin
from tools import eventbuilder
# pylint: enable=import-error


__version__ = "1.3.2"


# Initialize the logger
LOGGER = logging.getLogger(__name__)

PLUGIN = Plugin("Test", True, LOGGER, __file__)


@subscribe_to("system.onstart")
def start_func(key, data):
    """Test the 'onstart' event."""
    LOGGER.debug("I'm now doing something productive!")
    return True


@subscribe_to(["test", "test.1", "test.plugin"])
def test1(key, data):
    """Test various events."""
    for i in range(50):
        eventbuilder.Event(sender_id=PLUGIN.name,
                           keyword="wait").trigger()
    LOGGER.warn("Test1 successful!\n%s - %s", key, data)
    return True


@subscribe_to("test.2")
def test2(key, data):
    """Test the 'test.2' event."""
    LOGGER.warn("Test2 successful!\n%s - %s", key, data)
    return True


@subscribe_to("system.onexit")
def stop_func(key, data):
    """Test the 'onexit' event."""
    LOGGER.debug("I'm not doing anything productive anymore.")
    return True