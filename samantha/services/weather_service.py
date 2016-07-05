"""This plugin gives Samantha access to weather data."""

###############################################################################
#
# TODO: [ ]
#
###############################################################################


# standard library imports
import logging
import traceback

# related third party imports
import requests

# application specific imports
# pylint: disable=import-error
from core import subscribe_to
from services.service import BaseClass
from tools import eventbuilder
try:
    import variables_private
    API_KEY = variables_private.owm_key
    LOCATION = variables_private.owm_location
except (ImportError, AttributeError):
    variables_private = None
    API_KEY = None
    LOCATION = None
# pylint: enable=import-error


__version__ = "1.2.4"


# Initialize the logger
LOGGER = logging.getLogger(__name__)

if variables_private is None:
    LOGGER.exception("Couldn't access the private variables.")
if API_KEY is None:
    LOGGER.exception("Couldn't access the API-Key.")
if LOCATION is None:
    LOGGER.exception("Couldn't access the Location.")

SERVICE = BaseClass("Weather", True, LOGGER, __file__)


@subscribe_to(["onstart", "schedule_hour"])
def check_weather(key, data):
    """Check the weather."""
    LOGGER.debug("Checking the Weather..")
    try:
        req = requests.get("{baseurl}?{location}&{key}".format(
            baseurl="http://api.openweathermap.org/data/2.5/weather",
            location="id=" + LOCATION,
            key="appid=" + API_KEY),
                           timeout=3)
        if req.status_code == 200:
            eventbuilder.Event(sender_id=SERVICE.name,
                               keyword="weather",
                               data=req.json()).trigger()
            return True
    except Exception:
        LOGGER.exception("Exception while connecting to OWM:\n%s",
                         traceback.format_exc())
    return False
