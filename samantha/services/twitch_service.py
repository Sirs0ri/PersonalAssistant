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


__version__ = "1.2.9"

# Initialize the logger
LOGGER = logging.getLogger(__name__)

if variables_private is None:
    LOGGER.exception("Couldn't access the private variables.")
if SECRETS is None:
    LOGGER.exception("Couldn't access the API-Key and/or client-ID.")

SERVICE = BaseClass("Twitch", SECRETS is not None, LOGGER, __file__)

STREAM_LIST = {}


@subscribe_to(["system.onstart", "time.schedule.min"])
def check_followed_streams(key, data):
    """Check for new online streams on twitch.tv."""
    # Make the http-request
    url = "https://api.twitch.tv/kraken/streams/followed"
    req = requests.get(url, params=SECRETS)
    try:
        data = json.loads(req.text)
    except ValueError:
        # Thrown by json if parsing a string fails due to an invalid format.
        data = {}
        LOGGER.exception("The call to Twitch's API returned invalid data.")
    new_streamlist = {}
    # parse the data
    if "streams" in data:
        # If so, streams are available
        data = data["streams"]
        for item in data:
            # Get the account name (unique!) for the current item
            channelname = item["channel"]["name"] \
                .encode("utf-8").decode("utf-8")
            current_game = item["channel"]["game"] \
                .encode("utf-8").decode("utf-8")
            # save the stream's data in a new list
            new_streamlist[channelname] = item
            if channelname not in STREAM_LIST:
                # The stream came online since the last check
                LOGGER.debug(u"'%s' is now online. Playing '%s'",
                             channelname, current_game)
                eventbuilder.Event(
                    sender_id=SERVICE.name,
                    keyword="media.twitch.online.{}".format(channelname),
                    data=item).trigger()
            else:
                # The channel was already online at the last check
                if current_game == STREAM_LIST[channelname]["channel"]["game"]:
                    LOGGER.debug("'%s' is still playing '%s'.",
                                 channelname, current_game)
                else:
                    LOGGER.debug("'%s' is now playing '%s'",
                                 channelname, current_game)
                    eventbuilder.Event(
                        sender_id=SERVICE.name,
                        keyword="media.twitch.gamechange.{}".format(
                            channelname),
                        data=item).trigger()
                # remove the channel from STREAM_LIST so that it can be
                # refilled with the new data
                del STREAM_LIST[channelname]

    while len(STREAM_LIST) > 0:
        # STREAM_LIST now contains only those streams that were online
        # during the last check but have gone offline since.
        channelname, channeldata = STREAM_LIST.popitem()
        LOGGER.debug("'%s' is now offline.", channelname)
        eventbuilder.Event(
            sender_id=SERVICE.name,
            keyword="media.twitch.offline.{}".format(channelname),
            data=channeldata).trigger()

    # update the existing STREAM_LIST with the new streams
    for channelname in new_streamlist:
        STREAM_LIST[channelname] = new_streamlist[channelname]
    return True
