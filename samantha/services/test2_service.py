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
        keywords = ["test2", "service_test"]
        name = "Test2"
        super(Service, self).__init__(name=name, uid=uid, logger=LOGGER,
                                     keywords=keywords, file_path=__file__)

    def stop(self):
        LOGGER.debug("I'm not doing anything productive anymore.")
        super(Service, self).stop()
