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
from core import subscribe_to
from services.service import BaseClass
from tools import eventbuilder
try:
    import variables_private
    secrets = {
        "oauth_token": variables_private.twitch_oauth_token,
        "client_id": variables_private.twitch_client_id}
except (ImportError, AttributeError):
    variables_private = None
    secrets = None
# pylint: enable=import-error


__version__ = "1.2.3"

# Initialize the logger
LOGGER = logging.getLogger(__name__)

if variables_private is None:
    LOGGER.exception("Couldn't access the private variables.")
if secrets is None:
    LOGGER.exception("Couldn't access the API-Key and/or client-ID.")

SERVICE = BaseClass("Twitch", secrets is not None, LOGGER, __file__)

streamlist = []


@subscribe_to(["onstart", "schedule_min"])
def check_followed_streams(key, data):
    """Check for new online streams on twitch.tv."""
    global streamlist
    # Make the http-request
    url = "https://api.twitch.tv/kraken/streams/followed"
    req = requests.get(url, params=secrets)
    data = json.loads(req.text)
    new_streamlist = {}
    # parse the data
    if "streams" in data:
        # If so, streams are available
        data = data["streams"]
        for item in data:
            channelname = item["channel"]["name"]
            new_streamlist[channelname] = item
            if channelname not in streamlist:
                # That means the stream came online since the last check
                LOGGER.debug("'%s' is now online.", channelname)
                eventbuilder.Event(
                    sender_id=SERVICE.name,
                    keyword="media.twitch.online.{}".format(
                        item["channel"]["name"]),
                    data=item).trigger()
            else:
                LOGGER.debug("'%s' is still online.", channelname)
                # The stream is online and already was at the last check
                del streamlist[channelname]

    for channelname in streamlist:
        # self.streamlist now contains all those streams that were online
        # during the last check but have gone offline since.
        LOGGER.debug("'%s' is now offline.", channelname)
        eventbuilder.Event(
            sender_id=SERVICE.name,
            keyword="media.twitch.offline.{}".format(channelname),
            data=streamlist[channelname]).trigger()
    # update the existing streamlist with the new streams
    streamlist = new_streamlist
    return True
