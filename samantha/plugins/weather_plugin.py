"""This plugin gives Samantha access to weather data."""

###############################################################################
#
# TODO: [ ]
#
###############################################################################


# standard library imports
import logging
import time

# related third party imports
import requests

# application specific imports
from core import subscribe_to
from plugins.plugin import Plugin
from tools import eventbuilder
try:
    import variables_private
    SECRETS = {"id": variables_private.owm_location,
              "appid": variables_private.owm_key}
except (ImportError, AttributeError):
    variables_private = None
    SECRETS = None


__version__ = "1.3.4"


# Initialize the logger
LOGGER = logging.getLogger(__name__)

if variables_private is None:
    LOGGER.exception("Couldn't access the private variables.")
if SECRETS is None:
    LOGGER.exception("Couldn't access the API-Key and/or location.")

PLUGIN = Plugin("Weather", SECRETS is not None, LOGGER, __file__)


@subscribe_to(["system.onstart", "time.schedule.hour"])
def check_weather(key, data):
    """Check the weather."""
    LOGGER.debug("Checking the Weather..")
    url = "http://api.openweathermap.org/data/2.5/weather"
    req = None
    tries = 0
    while tries <= 3 and req is None:
        try:
            req = requests.get(url, params=SECRETS, timeout=15)
            if req.status_code == 200:
                tries = 0
                eventbuilder.Event(sender_id=PLUGIN.name,
                                   keyword="weather.update",
                                   data=req.json()).trigger()
                return "Weather updated successfully."
        except (requests.exceptions.ConnectionError,
                requests.exceptions.SSLError,
                requests.exceptions.Timeout), e:
            LOGGER.warn("Connecting to OWM failed on attempt %d. "
                        "Retrying in two seconds. Error: %s", tries, e)
            time.sleep(2)

    if req is None:
        LOGGER.exception("Connecting to OWM failed three times in a row.")
        return "Error: Connecting to OWM failed three times in a row."
