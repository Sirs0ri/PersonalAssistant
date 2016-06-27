"""A device to test loading devices. It doesn't do anything."""

###############################################################################
#
# TODO: [ ] docstrings
# TODO: [ ] comments
#
###############################################################################


# standard library imports
import logging

# related third party imports

# application specific imports
# pylint: disable=import-error
from devices.device import BaseClass
# pylint: enable=import-error


__version__ = "1.1.3"


# Initialize the logger
LOGGER = logging.getLogger(__name__)


class Device(BaseClass):
    """Just a test device without functionality."""

    def __init__(self, uid):
        """Initialize this device."""
        LOGGER.info("Initializing...")
        self.name = "Test"
        self.uid = uid
        self.keywords = ["test", "service_test"]
        LOGGER.debug("I'm now doing shit!")
        super(Device, self).__init__(
            logger=LOGGER, file_path=__file__, active=False)

    def stop(self):
        """Exit this device."""
        LOGGER.info("Exiting...")
        LOGGER.debug("I'm not doing shit anymore.")
        return super(Device, self).stop()
