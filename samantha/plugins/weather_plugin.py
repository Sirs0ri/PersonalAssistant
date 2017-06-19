"""This plugin gives Samantha access to weather data."""

###############################################################################
#
# TODO: [ ]
#
###############################################################################


# standard library imports
import configparser
import logging
import time

# related third party imports
import requests

# application specific imports
from samantha.core import subscribe_to
from samantha.plugins.plugin import Plugin
from samantha.tools import eventbuilder


__version__ = "1.4.0a1"


# Initialize the logger
LOGGER = logging.getLogger(__name__)

# TODO Wrap this in a function and make it callable via event
config = configparser.ConfigParser()
if config.read("variables_private.ini"):
    # this should be ['variables_private.ini'] if the config was found
    owm_config = config["openweathermap"]
    SECRETS = {"id": owm_config.get("location"),
               "appid": owm_config.get("api_key")
               }
else:
    LOGGER.warning("No config found! Are you sure the file %s exists?",
                   "samantha/variables_private.ini")
    SECRETS = None

PLUGIN = Plugin("Weather", SECRETS is not None, LOGGER, __file__)


@subscribe_to(["system.onstart", "time.schedule.hourly_rnd"])
def check_weather(key, data):
    """Check the weather."""
    LOGGER.debug("Checking the Weather..")
    url = "http://api.openweathermap.org/data/2.5/weather"
    req = None
    tries = 0
    errors = []
    while tries <= 3 and req is None:
        if tries > 0:
            LOGGER.debug("Retrying in %d seconds.", 15*tries)
            time.sleep(15 * tries)
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
                LOGGER.warning("The request returned the wrong status code: %s",
                               req.status_code)
                errors.append("Wrong statuscode: {}".format(req.status_code))
                req = None
        except (requests.exceptions.ConnectionError,
                requests.exceptions.SSLError,
                requests.exceptions.Timeout) as e:
            LOGGER.warning("Connecting to OWM failed on attempt %d. Error: %s",
                           tries, repr(e))
            errors.append(e.__repr__())
        except ValueError as e:
            LOGGER.warning("The requested data could not be processed "
                           "successfully. Error: %s", repr(e))
            errors.append(repr(e))

    if req is None:
        LOGGER.error("Connecting to OWM didn't return a valid result three "
                     "times in a row. Errors: %s", errors)
        return ("Error: Connecting to OWM didn't return a valid result three "
                "times in a row. Errors: %s" % errors)
    else:
        LOGGER.error("Connecting to OWM failed three times in a row even "
                     "though a connection was established. Errors: %s", errors)
