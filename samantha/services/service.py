"""Contains a baseclass for services."""

###############################################################################
#
# TODO: [ ]
#
###############################################################################


# standard library imports
import logging

# related third party imports

# application specific imports


__version__ = "1.2.2"


# Initialize the logger
LOGGER = logging.getLogger(__name__)


class BaseClass(object):
    """Baseclass, that holds the mandatory methods a device must support."""

    def __init__(self, name="Service", active=False, logger=None, file_path=None):
        """Set the service's attributes, if they're not set already."""
        self.name = name
        self.uid = "NO_UID"
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
        """Return a simple string representation of the service."""
        return "Service '{}', UID {}".format(self.name, self.uid)

    def __repr__(self):
        """Return a verbose string representation of the service."""
        return "Service '{}', UID {} from {}.".format(
            self.name, self.uid, self.path)
