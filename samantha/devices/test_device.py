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
        keywords = ["test1", "device_test"]
        name = "Test1"
        super(Device, self).__init__(name=name, uid=uid, logger=LOGGER,
                                     keywords=keywords, file_path=__file__)

    def stop(self):
        LOGGER.debug("I'm not doing shit anymore.")
        super(Device, self).stop()
