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

    def __init__(self, name="Device", uid="", keywords=[],
                 active=True, logger=None, file_path=None):
        self.name = name
        self.UID = uid
        self.KEYWORDS = keywords
        self.is_active = active
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
        return "Device '{}', UID {}".format(self.name, self.UID)

    def __repr__(self):
        return "Device '{}', UID {} from {}. Keywords: {}".format(
            self.name, self.UID, self.path, self.KEYWORDS)

    def stop(self):
        self.LOGGER.debug("Stopped successfully.")

    def process(self, key):
        self.LOGGER.warn("My process() function isn't implemented yet! "
                         "'%s' won't be processed.")
