""""""

###############################################################################
#
# TODO: [ ] docstrings
# TODO: [ ] comments
#
###############################################################################


from services.service import BaseClass

import logging


__version__ = "1.1.0"


# Initialize the logger
LOGGER = logging.getLogger(__name__)

class Service(BaseClass):

    def __init__(self, uid):
        LOGGER.info("Initializing...")
        self.name = "Test2"
        self.uid = uid
        self.keywords = ["test2", "service_test"]
        LOGGER.debug("I'm now doing something productive!")
        super(Service, self).__init__(
            logger=LOGGER, file_path=__file__, active=False)

    def stop(self):
        LOGGER.info("Exiting...")
        LOGGER.debug("I'm not doing anything productive anymore.")
        super(Service, self).stop()
