""""""

###############################################################################
#
# TODO: [ ] docstrings
# TODO: [ ] comments
#
###############################################################################


from services.service import BaseClass

import logging

# Initialize the logger
LOGGER = logging.getLogger(__name__)

class Service(BaseClass):

    def __init__(self, uid):
        LOGGER.debug("I'm now doing shit!")
        self.name = "Test"
        self.uid = uid
        self.keywords = ["test", "service_test"]
        super(Service, self).__init__(logger=LOGGER, file_path=__file__)

    def stop(self):
        LOGGER.debug("I'm not doing shit anymore.")
        super(Service, self).stop()
