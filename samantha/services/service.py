""""""

###############################################################################
#
# TODO: [ ] docstrings
# TODO: [ ] comments
#
###############################################################################


import logging

# Initialize the logger
LOGGER = logging.getLogger(__name__)


class BaseClass(object):

    def __init__(self, active=True, logger=None, file_path=None):
        if not hasattr(self, "name"):
            self.name = "Service"
        if not hasattr(self, "uid"):
            self.uid = "NO_UID"
        if not hasattr(self, "keywords"):
            self.keywords = []
        self.is_active = active
        if logger:
            self.LOGGER = logger
        else:
            self.LOGGER = LOGGER
        if file_path:
            self.path = file_path
        else:
            self.path = __file__
        self.LOGGER.info("Initialisation complete")

    def __str__(self):
        return "Service '{}', UID {}".format(self.name, self.uid)

    def __repr__(self):
        return "Service '{}', UID {} from {}. Keywords: {}".format(
            self.name, self.uid, self.path, self.keywords)

    def stop(self):
        self.LOGGER.info("Exited.")

    def process(self, key, data=None):
        self.LOGGER.warn("My process() function isn't implemented yet! "
                         "'%s' won't be processed.", key)
