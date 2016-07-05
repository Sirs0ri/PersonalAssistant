"""A service to test loading services. It doesn't do anything."""

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
from services.service import BaseClass
from tools import SleeperThread
# pylint: enable=import-error


__version__ = "1.3.1"

# Initialize the logger
LOGGER = logging.getLogger(__name__)

service = BaseClass("Test", True, LOGGER, __file__)


@subscribe_to("onstart")
def start_func(key, data):
    LOGGER.debug("I'm now doing something productive!")
    return True


@subscribe_to("test")
def test(key, data):
    def function():
        """Print "Heyho!" and a bunch of ~ around."""
        print "~"*30
        print "Heyho!"
        print "~"*30
    thread = SleeperThread(delay=7, target=function)
    thread.start()
    return True


@subscribe_to("onexit")
def stop_func(key, data):
    LOGGER.debug("I'm not doing anything productive anymore.")
    return True


# class Service(BaseClass):
#     """Just a test service without functionality."""
#
#     def __init__(self, uid):
#         """Initialize this device."""
#         LOGGER.info("Initializing...")
#         self.name = "Test"
#         self.uid = uid
#         self.keywords = ["onstart", "test", "onexit"]
#         LOGGER.debug("I'm now doing shit!")
#         super(Service, self).__init__(
#             logger=LOGGER, file_path=__file__, active=True)
#
#     def stop(self):
#         """Exit this device."""
#         LOGGER.info("Exiting...")
#         LOGGER.debug("I'm not doing shit anymore.")
#         return super(Service, self).stop()
#
#     def process(self, key, data=None):
#         """Process a command from the core."""
#         if key == "test":
#             thread = SleeperThread(delay=7, target=function)
#             thread.start()
#         else:
#             LOGGER.warn("Keyword not in use. (%s, %s)", key, data)
