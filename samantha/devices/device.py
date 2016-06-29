"""Contains a baseclass for devices."""

###############################################################################
#
# TODO: [ ] default methods
#
###############################################################################


# standard library imports
import logging

# related third party imports

# application specific imports


__version__ = "1.1.10"


# Initialize the logger
LOGGER = logging.getLogger(__name__)


class BaseClass(object):
    """Baseclass, that holds the mandatory methods a device must support."""

    def __init__(self, active=True, logger=None, file_path=None):
        """Set the device's attributes, if they're not set already."""
        if not hasattr(self, "name"):
            self.name = "Device"
        if not hasattr(self, "uid"):
            self.uid = "NO_UID"
        if not hasattr(self, "keywords"):
            self.keywords = []
        self.is_active = active
        if logger:
            self.logger = logger
        else:
            self.logger = LOGGER
        if file_path:
            self.path = file_path
        else:
            self.path = __file__
        self.logger.info("Initialisation complete")

    def __str__(self):
        """Return a simple string representation of the device."""
        return "Device '{}', UID {}".format(self.name, self.uid)

    def __repr__(self):
        """Return a verbose string representation of the device."""
        return "Device '{}', UID {}. Loaded from {}. Keywords: {}".format(
            self.name, self.uid, self.path, self.keywords)

    def stop(self):
        """Cleanly exit the device."""
        self.logger.info("Exited.")
        return True

    def process(self, key, data=None):
        """Process a command from the core."""
        self.logger.warn("My process() function isn't implemented yet! "
                         "'%s, %s' won't be processed.", key, data)
