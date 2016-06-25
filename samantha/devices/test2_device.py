""""""

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


__version__ = "1.1.1"


# Initialize the logger
LOGGER = logging.getLogger(__name__)


class Device(BaseClass):

    def __init__(self, uid):
        LOGGER.info("Initializing...")
        self.name = "Test2"
        self.uid = uid
        self.keywords = ["test2", "service_test"]
        LOGGER.debug("I'm now doing something productive!")
        super(Device, self).__init__(
            logger=LOGGER, file_path=__file__, active=False)

    def stop(self):
        LOGGER.info("Exiting...")
        LOGGER.debug("I'm not doing anything productive anymore.")
        super(Device, self).stop()
