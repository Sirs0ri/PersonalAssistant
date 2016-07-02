"""A service to test loading services. It doesn't do anything."""

###############################################################################
#
# TODO: [ ] Events when streams go offline
#
###############################################################################


# standard library imports
import json
import logging

# related third party imports
import requests

# application specific imports
# pylint: disable=import-error
from services.service import BaseClass
from tools import eventbuilder
try:
    import variables_private
except ImportError:
    variables_private = None
# pylint: enable=import-error


__version__ = "1.0.0"

# Initialize the logger
LOGGER = logging.getLogger(__name__)


class Service(BaseClass):
    """Service that checks for online streams on twitch.tv."""

    def __init__(self, uid):
        """Initialize this device."""
        LOGGER.info("Initializing...")
        self.name = "Twitch"
        self.uid = uid
        self.keywords = ["onstart", "schedule_min"]
        self.url = "https://api.twitch.tv/kraken/streams/followed"
        self.streamlist = []
        try:
            self.url_params = {
                "oauth_token": variables_private.twitch_oauth_token,
                "client_id": variables_private.twitch_client_id}
            active = True
        except AttributeError:
            LOGGER.exception("Couldn't access the API-Key and/or client-ID.")
            self.url_params = None
            active = False
        self.weather = None
        super(Service, self).__init__(
            logger=LOGGER, file_path=__file__, active=active)

    def check_followed_streams(self):
        """Check for new online streams on twitch.tv."""
        # Make the http-request
        req = requests.get(self.url, params=self.url_params)
        data = json.loads(req.text)
        new_streamlist = {}
        # parse the data
        if "streams" in data:
            # If so, streams are available
            data = data["streams"]
            for item in data:
                new_streamlist[item["channel"]["name"]] = item
                if item["channel"]["name"] not in self.streamlist:
                    # That means the stream came online since the last check
                    eventbuilder.Event(sender_id=self.name,
                                       keyword="media.twitch.online.{}".format(
                                           item["channel"]["name"]),
                                       data=item).trigger()
        # update the existing streamlist with the new streams
        self.streamlist = new_streamlist

    def stop(self):
        """Exit this device."""
        LOGGER.info("Exiting...")
        return super(Service, self).stop()

    def process(self, key, data=None):
        """Process a command from the core."""
        if key in ["onstart", "schedule_min"]:
            return self.check_followed_streams()
        else:
            LOGGER.warn("Keyword not in use. (%s, %s)", key, data)
