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
from core import subscription
from devices.device import BaseClass
# pylint: enable=import-error


__version__ = "1.2.0"


# Initialize the logger
LOGGER = logging.getLogger(__name__)

device = BaseClass("Test", True, LOGGER, __file__)


@subscription.start
def start_func(key, data):
    LOGGER.debug("I'm now doing something productive!")
    return True


@subscription.event(["test", "test.1", "test.device"])
def test1(key, data):
    LOGGER.warn("Test1 successful!\n%s - %s", key, data)
    return True


@subscription.event("test.2")
def test2(key, data):
    LOGGER.warn("Test2 successful!\n%s - %s", key, data)
    return True


@subscription.exit
def stop_func(key, data):
    LOGGER.debug("I'm not doing anything productive anymore.")
    return True


# class Device(BaseClass):
#     """Just another test device without functionality."""
#
#     def __init__(self, uid):
#         """Initialize this device."""
#         LOGGER.info("Initializing...")
#         self.name = "Test1"
#         self.uid = uid
#         self.keywords = ["test1", "service_test"]
#         LOGGER.debug("I'm now doing something productive!")
#         super(Device, self).__init__(
#             logger=LOGGER, file_path=__file__, active=False)
#
#     def stop(self):
#         """Exit this device."""
#         LOGGER.info("Exiting...")
#         LOGGER.debug("I'm not doing anything productive anymore.")
#         return super(Device, self).stop()
