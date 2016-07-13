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
from plugins.plugin import Plugin
from tools import eventbuilder
try:
    import variables_private
    API_KEY = variables_private.owm_key
    LOCATION = variables_private.owm_location
except (ImportError, AttributeError):
    variables_private = None
    API_KEY = ""
    LOCATION = ""
# pylint: enable=import-error


__version__ = "1.3.1"


# Initialize the logger
LOGGER = logging.getLogger(__name__)

if variables_private is None:
    LOGGER.exception("Couldn't access the private variables.")
if API_KEY is "":
    LOGGER.exception("Couldn't access the API-Key.")
if LOCATION is "":
    LOGGER.exception("Couldn't access the Location.")

PLUGIN = Plugin("Weather", True, LOGGER, __file__)


@subscribe_to(["system.onstart", "time.schedule.hour"])
def check_weather(key, data):
    """Check the weather."""
    LOGGER.debug("Checking the Weather..")
    try:
        req = requests.get("{baseurl}?{location}&{key}".format(
            baseurl="http://api.openweathermap.org/data/2.5/weather",
            location="id={}".format(LOCATION),
            key="appid={}".format(API_KEY)),
                           timeout=15)
        if req.status_code == 200:
            eventbuilder.Event(sender_id=PLUGIN.name,
                               keyword="weather.update",
                               data=req.json()).trigger()
            return True
    except Exception:
        LOGGER.exception("Exception while connecting to OWM:\n%s",
                         traceback.format_exc())
    return False
