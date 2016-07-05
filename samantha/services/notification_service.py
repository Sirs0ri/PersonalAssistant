"""Another test device to test loading devices."""

###############################################################################
#
# TODO: [ ]
#
###############################################################################


# standard library imports
import logging

# related third party imports

# application specific imports
# pylint: disable=import-error
from core import subscribe_to
from services.service import BaseClass
# pylint: enable=import-error


__version__ = "1.2.2"


# Initialize the logger
LOGGER = logging.getLogger(__name__)

SERVICE = BaseClass("Notification", False, LOGGER, __file__)
