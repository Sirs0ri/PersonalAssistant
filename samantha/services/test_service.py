""""""

###############################################################################
#
# TODO: [ ] docstrings
# TODO: [ ] comments
#
###############################################################################


from services.service import BaseClass
from tools import Sleeper_Thread


import logging


__version__ = "1.2.0"

# Initialize the logger
LOGGER = logging.getLogger(__name__)


def function():
    print "~"*30
    print "Heyho!"
    print "~"*30

class Service(BaseClass):

    def __init__(self, uid):
        LOGGER.info("Initializing...")
        self.name = "Test"
        self.uid = uid
        self.keywords = ["onstart"]
        LOGGER.debug("I'm now doing shit!")
        super(Service, self).__init__(
            logger=LOGGER, file_path=__file__, active=False)

    def stop(self):
        LOGGER.info("Exiting...")
        LOGGER.debug("I'm not doing shit anymore.")
        super(Service, self).stop()

    def process(self, key, data=None):
        if key == "onstart":
            t = Sleeper_Thread(delay=30, target=function)
            t.start()
