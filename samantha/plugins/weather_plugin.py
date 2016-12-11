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
from samantha.core import subscribe_to
from samantha.plugins.plugin import Plugin
from samantha.tools import eventbuilder
try:
    import samantha.variables_private as variables_private
    SECRETS = {"id": variables_private.owm_location,
              "appid": variables_private.owm_key}
except (ImportError, AttributeError):
    variables_private = None
    SECRETS = None


__version__ = "1.3.11"


# Initialize the logger
LOGGER = logging.getLogger(__name__)

if variables_private is None:
    LOGGER.error("Couldn't access the private variables.")
if SECRETS is None:
    LOGGER.error("Couldn't access the API-Key and/or location.")

PLUGIN = Plugin("Weather", SECRETS is not None, LOGGER, __file__)


@subscribe_to(["system.onstart", "time.schedule.hour"])
def check_weather(key, data):
    """Check the weather."""
    LOGGER.debug("Checking the Weather..")
    url = "http://api.openweathermap.org/data/2.5/weather"
    req = None
    tries = 0
    errors = []
    while tries <= 3 and req is None:
        if tries > 0:
            LOGGER.debug("Retrying in 15 seconds.")
            time.sleep(15)
        try:
            tries += 1
            req = requests.get(url, params=SECRETS, timeout=15)
            if req.status_code == 200:
                new_data = req.json()
                eventbuilder.eEvent(sender_id=PLUGIN.name,
                                    keyword="weather.update",
                                    data=new_data).trigger()
                for category in new_data:
                    eventbuilder.eEvent(sender_id=PLUGIN.name,
                                        keyword="weather.{}.update".format(
                                           category),
                                        data=new_data[category]).trigger()
                return "Weather updated successfully."
            else:
                LOGGER.warn("The request returned the wrong status code: %s",
                            req.status_code)
                req = None
        except (requests.exceptions.ConnectionError,
                requests.exceptions.SSLError,
                requests.exceptions.Timeout), e:
            LOGGER.warn("Connecting to OWM failed on attempt %d. Error: %s",
                        tries, e)
            errors.append(e.__repr__())
        except ValueError, e:
            LOGGER.warn("The requested data could not be processed "
                        "successfully. Error: %s", e)
            errors.append(e.__repr__())

    if req is None:
        LOGGER.error("Connecting to OWM didn't return a valid result three "
                     "times in a row. Errors: %s", errors)
        return ("Error: Connecting to OWM didn't return a valid result three "
                "times in a row. Errors: %s" % errors)
    else:
        LOGGER.error("Connecting to OWM failed three times in a row even "
                     "though a connection was established. Errors: %s", errors)
