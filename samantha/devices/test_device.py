"""A device to test loading devices. It doesn't do anything."""

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
from devices.device import BaseClass
# pylint: enable=import-error


__version__ = "1.2.3"


# Initialize the logger
LOGGER = logging.getLogger(__name__)

DEVICE = BaseClass("Test", True, LOGGER, __file__)


@subscribe_to("onstart")
def start_func(key, data):
    LOGGER.debug("I'm now doing something productive!")
    return True


@subscribe_to(["test", "test.1", "test.device"])
def test1(key, data):
    LOGGER.warn("Test1 successful!\n%s - %s", key, data)
    return True


@subscribe_to("test.2")
def test2(key, data):
    LOGGER.warn("Test2 successful!\n%s - %s", key, data)
    return True


@subscribe_to("onexit")
def stop_func(key, data):
    LOGGER.debug("I'm not doing anything productive anymore.")
    return True
