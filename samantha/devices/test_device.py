""""""

###############################################################################
#
# TODO: [ ] docstrings
# TODO: [ ] comments
#
###############################################################################


from devices.device import BaseClass

import logging

# Initialize the logger
LOGGER = logging.getLogger(__name__)

class Device(BaseClass):

    def __init__(self, uid):
        LOGGER.debug("I'm now doing shit!")
        self.name = "Test"
        self.uid = uid
        self.keywords = ["test", "service_test"]
        super(Device, self).__init__(logger=LOGGER, file_path=__file__)

    def stop(self):
        LOGGER.debug("I'm not doing shit anymore.")
        super(Device, self).stop()
