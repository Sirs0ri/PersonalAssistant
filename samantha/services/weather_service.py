"""
This plugin gives Samantha access to weather data,
as well as dates for sunrise/sunset.
"""

###############################################################################
#
# TODO: [ ] docstrings
# TODO: [ ] comments
#
###############################################################################


import requests

import logging
from services.service import BaseClass
import tools
try:
    import variables_private
except ImportError:
    variables_private = None


__version__ = "1.1.0"


# Initialize the logger
LOGGER = logging.getLogger(__name__)


class Service(BaseClass):

    def __init__(self, uid):
        LOGGER.info("Initializing...")
        self.name = "Weather"
        self.uid = uid
        self.keywords = ["onstart", "schedule_hour"]
        try:
            self.api_key = variables_private.owm_key
            self.location = variables_private.owm_location
            active = True
        except Exception as e:
            LOGGER.exception("Couldn't access the API-Key and/or location.")
            self.api_key = ""
            self.location = ""
            active = False
        self.weather = None
        super(Service, self).__init__(
            logger=LOGGER, file_path=__file__, active=active)

    def process(self, key, data=None):
        if key in ["onstart", "schedule_hour"]:
            LOGGER.debug("Checking the Weather..")
            req = requests.get("{baseurl}?id={location}&appid={key}".format(
                baseurl="http://api.openweathermap.org/data/2.5/weather",
                location=self.location,
                key=self.api_key))
            if req.status_code == 200:
                tools.eventbuilder.Event(sender_id=self.name,
                                         keyword="weather",
                                         data=req.json()).trigger()
                return True
        else:
            LOGGER.warn("Keyword not in use. (%s, %s)", key, data)
        return False
