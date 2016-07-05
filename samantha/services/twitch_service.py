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
    SECRETS = {
        "oauth_token": variables_private.twitch_oauth_token,
        "client_id": variables_private.twitch_client_id}
except (ImportError, AttributeError):
    variables_private = None
    SECRETS = None
# pylint: enable=import-error


__version__ = "1.2.4"

# Initialize the logger
LOGGER = logging.getLogger(__name__)

if variables_private is None:
    LOGGER.exception("Couldn't access the private variables.")
if SECRETS is None:
    LOGGER.exception("Couldn't access the API-Key and/or client-ID.")

SERVICE = BaseClass("Twitch", SECRETS is not None, LOGGER, __file__)

STREAM_LIST = []


@subscribe_to(["onstart", "schedule_min"])
def check_followed_streams(key, data):
    """Check for new online streams on twitch.tv."""
    global STREAM_LIST
    # Make the http-request
    url = "https://api.twitch.tv/kraken/streams/followed"
    req = requests.get(url, params=SECRETS)
    data = json.loads(req.text)
    new_streamlist = {}
    # parse the data
    if "streams" in data:
        # If so, streams are available
        data = data["streams"]
        for item in data:
            channelname = item["channel"]["name"]
            new_streamlist[channelname] = item
            if channelname not in STREAM_LIST:
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
                del STREAM_LIST[channelname]

    for channelname in STREAM_LIST:
        # STREAM_LIST now contains all those streams that were online
        # during the last check but have gone offline since.
        LOGGER.debug("'%s' is now offline.", channelname)
        eventbuilder.Event(
            sender_id=SERVICE.name,
            keyword="media.twitch.offline.{}".format(channelname),
            data=STREAM_LIST[channelname]).trigger()
    # update the existing STREAM_LIST with the new streams
    STREAM_LIST = new_streamlist
    return True
