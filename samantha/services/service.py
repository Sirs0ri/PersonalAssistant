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

    def __init__(self, name="Service", uid="", keywords=[],
                 active=True, logger=None, file_path=None):
        self.name = name
        self.UID = uid
        self.KEYWORDS = keywords
        self.ACTIVE = active
        if logger:
            self.LOGGER = logger
        else:
            self.LOGGER = LOGGER
        if file_path:
            self.path = file_path
        else:
            self.path = __file__
        self.LOGGER.debug("Initialisation complete")

    def __str__(self):
        return "Service '{}', UID {}".format(self.name, self.UID)

    def __repr__(self):
        return "Service '{}', UID {} from {}. Keywords: {}".format(
            self.name, self.UID, self.path, self.KEYWORDS)

    def stop(self):
        self.LOGGER.debug("Stopped successfully.")
