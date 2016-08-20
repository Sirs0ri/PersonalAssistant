"""A service to test loading services. It doesn't do anything."""

###############################################################################
#
# TODO: [ ] Events when streams go offline
#
###############################################################################


# standard library imports
import json
import logging
import time

# related third party imports
import requests

# application specific imports
import samantha.context as context
from samantha.core import subscribe_to
from samantha.plugins.plugin import Plugin
from samantha.tools import eventbuilder
try:
    import samantha.variables_private as variables_private
    SECRETS = {
        "oauth_token": variables_private.twitch_oauth_token,
        "client_id": variables_private.twitch_client_id}
except (ImportError, AttributeError):
    variables_private = None
    SECRETS = None


__version__ = "1.3.15"

# Initialize the logger
LOGGER = logging.getLogger(__name__)

if variables_private is None:
    LOGGER.error("Couldn't access the private variables.")
if SECRETS is None:
    LOGGER.error("Couldn't access the API-Key and/or client-ID.")

PLUGIN = Plugin("Twitch", SECRETS is not None, LOGGER, __file__)

STREAM_LIST = context.get_children("media.twitch", default={})


@subscribe_to(["system.onstart", "time.schedule.min"])
def check_followed_streams(key, data):
    """Check for new online streams on twitch.tv."""
    # Make the http-request
    url = "https://api.twitch.tv/kraken/streams/followed"
    req = None
    tries = 0
    while tries <= 3 and req is None:
        try:
            tries += 1
            req = requests.get(url, params=SECRETS, timeout=15)
            tries = 0
        except (requests.exceptions.ConnectionError,
                requests.exceptions.SSLError,
                requests.exceptions.Timeout), e:
            LOGGER.warn("Connecting to Twitch failed on attempt %d. "
                        "Retrying in two seconds. Error: %s", tries, e)
            time.sleep(2)

    if req is None:
        LOGGER.error("Connecting to Twitch failed three times in a row.")
        return "Error: Connecting to Twitch failed three times in a row."

    # Replace null-fields with "null"-strings
    text = req.text.replace('null', '"null"')
    try:
        data = json.loads(text)
    except ValueError, e:
        # Thrown by json if parsing a string fails due to an invalid format.
        LOGGER.error("The call to Twitch's API returned invalid data. "
                     "Error: %s Data: %s", e, text)
        return "Error: The call to Twitch's API returned invalid data."
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
            if (channelname not in STREAM_LIST or
                STREAM_LIST[channelname] is None):
                # The stream came online since the last check
                LOGGER.debug(u"'%s' is now online. Playing '%s'",
                             channelname, current_game)
                eventbuilder.eEvent(
                    sender_id=PLUGIN.name,
                    keyword="media.twitch.availability.online.{}".format(
                        channelname),
                    data=item).trigger()
                context.set_property(
                    "media.twitch.{}".format(channelname), item)
                if channelname in STREAM_LIST:
                    # remove the channel from STREAM_LIST so that it can be
                    # refilled with the new data
                    del STREAM_LIST[channelname]
            else:
                # The channel was already online at the last check
                if current_game == STREAM_LIST[channelname]["channel"]["game"]:
                    # The game hasn't changed
                    LOGGER.debug("'%s' is still playing '%s'.",
                                 channelname, current_game)
                else:
                    # The game changed
                    LOGGER.debug("'%s' is now playing '%s'",
                                 channelname, current_game)
                    eventbuilder.eEvent(
                        sender_id=PLUGIN.name,
                        keyword="media.twitch.gamechange.{}".format(
                            channelname),
                        data=item).trigger()
                    context.set_property(
                        "media.twitch.{}".format(channelname), item)
                # remove the channel from STREAM_LIST so that it can be
                # refilled with the new data
                del STREAM_LIST[channelname]
    else:
        LOGGER.warn("The data didn't include the 'streams' field.")
        return "Error: The data didn't include the 'streams' field."

    while len(STREAM_LIST) > 0:
        # STREAM_LIST now contains only those streams that were online
        # during the last check but have gone offline since.
        channelname, channeldata = STREAM_LIST.popitem()
        if channeldata is not None:
            LOGGER.debug("'%s' is now offline.", channelname)
            key = "media.twitch.availability.offline.{}".format(channelname)
            eventbuilder.eEvent(sender_id=PLUGIN.name,
                                keyword=key,
                                data=channeldata).trigger()
            context.set_property(
                "media.twitch.{}".format(channelname), None)

    # update the existing STREAM_LIST with the new streams
    for channelname in new_streamlist:
        STREAM_LIST[channelname] = new_streamlist[channelname]
    return "Streams updated successfully."
