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
        LOGGER.debug("I'm now doing something productive!")
        self.name = "Test2"
        self.uid = uid
        self.keywords = ["test2", "service_test"]
        super(Service, self).__init__(logger=LOGGER, file_path=__file__)

    def stop(self):
        LOGGER.debug("I'm not doing anything productive anymore.")
        super(Service, self).stop()
