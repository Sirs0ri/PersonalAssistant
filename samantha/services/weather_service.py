"""This plugin gives Samantha access to weather data."""

###############################################################################
#
# TODO: [ ] docstrings
# TODO: [ ] comments
#
###############################################################################


# standard library imports
import logging
import requests
import traceback

# related third party imports

# application specific imports
# pylint: disable=import-error
from services.service import BaseClass
import tools
try:
    import variables_private
except ImportError:
    variables_private = None
# pylint: enable=import-error


__version__ = "1.1.5"


# Initialize the logger
LOGGER = logging.getLogger(__name__)


class Service(BaseClass):
    """Service that implements the Open Weather Map API."""

    def __init__(self, uid):
        """Initialize the service."""
        LOGGER.info("Initializing...")
        self.name = "Weather"
        self.uid = uid
        self.keywords = ["onstart", "schedule_hour"]
        try:
            self.api_key = variables_private.owm_key
            self.location = variables_private.owm_location
            active = True
        except Exception:
            LOGGER.exception("Couldn't access the API-Key and/or location.")
            self.api_key = ""
            self.location = ""
            active = False
        self.weather = None
        super(Service, self).__init__(
            logger=LOGGER, file_path=__file__, active=active)

    def process(self, key, data=None):
        """Process an event from the core."""
        if key in ["onstart", "schedule_hour"]:
            LOGGER.debug("Checking the Weather..")
            try:
                req = requests.get("{baseurl}?{location}&{key}".format(
                    baseurl="http://api.openweathermap.org/data/2.5/weather",
                    location="id=" + self.location,
                    key="appid=" + self.api_key),
                                   timeout=3)
                if req.status_code == 200:
                    tools.eventbuilder.Event(sender_id=self.name,
                                             keyword="weather",
                                             data=req.json()).trigger()
                    return True
            except Exception:
                LOGGER.exception("Exception while connecting to OWM:\n%s",
                                 traceback.format_exc())
                return False
        else:
            LOGGER.warn("Keyword not in use. (%s, %s)", key, data)
        return False
