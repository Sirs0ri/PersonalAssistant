"""Another test device to test loading devices."""

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
from services.service import BaseClass
# pylint: enable=import-error


__version__ = "1.1.4"


# Initialize the logger
LOGGER = logging.getLogger(__name__)


class Service(BaseClass):
    """Just another test device without functionality."""

    def __init__(self, uid):
        """Initialize the service."""
        LOGGER.info("Initializing...")
        self.name = "Test2"
        self.uid = uid
        self.keywords = ["test2", "service_test"]
        LOGGER.debug("I'm now doing something productive!")
        super(Service, self).__init__(
            logger=LOGGER, file_path=__file__, active=False)

    def stop(self):
        """Exit this device."""
        LOGGER.info("Exiting...")
        LOGGER.debug("I'm not doing anything productive anymore.")
        return super(Service, self).stop()
