"""A plugin to test loading devices. It doesn't do anything."""

###############################################################################
#
# TODO: [ ]
#
###############################################################################


# standard library imports
import logging

# related third party imports

# application specific imports
import samantha.context as context
from samantha.core import subscribe_to
from samantha.tools import eventbuilder
from samantha.plugins.plugin import Plugin


__version__ = "1.0.10"

# Initialize the logger
LOGGER = logging.getLogger(__name__)

PLUGIN = Plugin("Mediacenter", True, LOGGER, __file__)

CC_DISPLAY_NAME = ""
CC_CONTENT_TYPE = "audio"
CC_PLAYER_STATE = ""


@subscribe_to(["chromecast.connection_change",
               "chromecast.playstate_change",
               "chromecast.contenttype_change"])
def update(key, data):
    global CC_CONTENT_TYPE, CC_DISPLAY_NAME, CC_PLAYER_STATE
    updated = False
    invalid = True
    if "content_type" in data and data["content_type"]:
        # playstate_change
        invalid = False
        if not data["content_type"] == CC_CONTENT_TYPE:
            CC_CONTENT_TYPE = data["content_type"]
            updated = True
            LOGGER.debug("Updated CC_CONTENT_TYPE to '%s'.", CC_CONTENT_TYPE)
    if "player_state" in data and data["player_state"]:
        invalid = False
        if not data["player_state"] == CC_PLAYER_STATE:
            CC_PLAYER_STATE = data["player_state"] or ""
            updated = True
            LOGGER.debug("Updated CC_PLAYER_STATE to '%s'.", CC_PLAYER_STATE)
    if "display_name" in data and data["display_name"]:
        invalid = False
        if not data["display_name"] == CC_DISPLAY_NAME:
            CC_DISPLAY_NAME = data["display_name"] or ""
            updated = True
            LOGGER.debug("Updated CC_DISPLAY_NAME to '%s'.", CC_DISPLAY_NAME)
    if invalid:
        return ("Error: Invalid Data. 'content_type', 'player_state' and "
                "'display_name' were all missing or empty.")
    if updated:
        if CC_CONTENT_TYPE and "audio" not in CC_CONTENT_TYPE:
            # Ignore the updates while Audio is playing. This is only
            # supposed to dim the lights while videos are playing.
            if context.get_value("time.time_of_day") == "night":
                if (CC_PLAYER_STATE in ["PLAYING", "BUFFERING"] and
                        CC_DISPLAY_NAME not in [None, "Backdrop"]):
                    # An app is playing video.
                    eventbuilder.eEvent(  # Turn on ambient light
                        sender_id=PLUGIN.name,
                        keyword="turn.on.ambient.light").trigger()
                    return "Ambient light turned on."
                else:
                    # No app connected or video is paused
                    eventbuilder.eEvent(  # Turn off ambient light
                        sender_id=PLUGIN.name,
                        keyword="turn.off.ambient.light").trigger()
                    return "Ambient light turned off."
            else:
                eventbuilder.eEvent(  # Turn off all light
                    sender_id=PLUGIN.name,
                    keyword="turn.off.light").trigger()
                return "It's daytime. The light is supposed to stay off."
        else:
            return "No video is playing. Not changing the light."
    else:
        return "No relevant information was updated. Not changing the light."
