""""""

###############################################################################
#
# TODO: [ ] docstrings
# TODO: [ ] comments
#
###############################################################################


from devices.device import BaseClass

import logging


__version__ = "1.1.0"


# Initialize the logger
LOGGER = logging.getLogger(__name__)

class Device(BaseClass):

    def __init__(self, uid):
        LOGGER.info("Initializing...")
        self.name = "Test"
        self.uid = uid
        self.keywords = ["test", "service_test"]
        LOGGER.debug("I'm now doing shit!")
        super(Device, self).__init__(
            logger=LOGGER, file_path=__file__, active=False)

    def stop(self):
        LOGGER.info("Exiting...")
        LOGGER.debug("I'm not doing shit anymore.")
        super(Device, self).stop()
