"""A plugin to test loading devices. It doesn't do anything."""

###############################################################################
#
# TODO: [ ]
#
###############################################################################


# standard library imports
import logging
from threading import Timer

# related third party imports

# application specific imports
from core import subscribe_to
from plugins.plugin import Device


__version__ = "1.4.4"

# Initialize the logger
LOGGER = logging.getLogger(__name__)

PLUGIN = Device("Test", True, LOGGER, __file__)


@subscribe_to("system.onstart")
def start_func(key, data):
    """Test the 'onstart' event."""
    LOGGER.debug("I'm now doing something productive!")
    return "I'm now doing something productive!"


@subscribe_to("test")
def test(key, data):
    """Test the 'test' event."""
    def function():
        """Print "Heyho!" and a bunch of ~ around."""
        print "~"*30
        print "Heyho! My command was {}.".format(key)
        print data
        print "~"*30
    thread = Timer(interval=7.0, target=function)
    thread.start()
    return "Processed the command {}.".format(key)


@subscribe_to("system.onexit")
def stop_func(key, data):
    """Test the 'onexit' event."""
    LOGGER.debug("I'm not doing anything productive anymore.")
    return "I'm not doing anything productive anymore."
