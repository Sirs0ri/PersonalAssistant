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


__version__ = "1.0.7"

# Initialize the logger
LOGGER = logging.getLogger(__name__)

PLUGIN = Plugin("Mediacenter", True, LOGGER, __file__)

CC_DISPLAY_NAME = None
CC_CONTENT_TYPE = None
CC_PLAYER_STATE = None


@subscribe_to(["chromecast.connection_change",
               "chromecast.playstate_change",
               "chromecast.contenttype_change"])
def update(key, data):
    global CC_CONTENT_TYPE, CC_DISPLAY_NAME, CC_PLAYER_STATE
    updated = False
    invalid = True
    if "content_type" in data:
        # playstate_change
        invalid = False
        if not data["content_type"] == CC_CONTENT_TYPE:
            CC_CONTENT_TYPE = data["content_type"]
            updated = True
            LOGGER.debug("Updated CC_CONTENT_TYPE to %s.", CC_CONTENT_TYPE)
    if "player_state" in data:
        invalid = False
        if not data["player_state"] == CC_PLAYER_STATE:
            CC_PLAYER_STATE = data["player_state"]
            updated = True
            LOGGER.debug("Updated CC_PLAYER_STATE to %s.", CC_PLAYER_STATE)
    if "display_name" in data:
        invalid = False
        if not data["display_name"] == CC_DISPLAY_NAME:
            CC_DISPLAY_NAME = data["display_name"]
            updated = True
            LOGGER.debug("Updated CC_DISPLAY_NAME to %s.", CC_DISPLAY_NAME)
    if invalid:
        return ("Error: Invalid Data. 'content_type', 'player_state' and "
                "'display_name' were all missing.")
    if updated:
        if context.get_value("time.time_of_day") == "night":
            if "audio" not in CC_CONTENT_TYPE:
                # Ignore the updates while Audio is playing. This is only
                # supposed to dim the lights while videos are playing.
                if (CC_PLAYER_STATE == "PLAYING" and
                        CC_DISPLAY_NAME not in [None, "Backdrop"]):
                    # An app is playing video.
                    eventbuilder.eEvent(  # Turn on ambient light
                        sender_id=PLUGIN.name,
                        keyword="turn.on.ambient.light").trigger()
                    return "Ambient light turned on."
                else:
                    # No app connected or video is paused
                    eventbuilder.eEvent(  # Turn off ambient 433-light
                        sender_id=PLUGIN.name,
                        keyword="turn.off.ambient.433").trigger()
                    eventbuilder.eEvent(  # Set LEDs to max brightness
                        sender_id=PLUGIN.name,
                        keyword="turn.on.led").trigger()
                    return "Ambient light turned off."
            else:
                return "No video is playing. Not changing the light."
        else:
            eventbuilder.eEvent(  # Turn off all light
                sender_id=PLUGIN.name,
                keyword="turn.off.light").trigger()
            return "It's daytime. The light is supposed to stay off."
    else:
        return "No relevant information was updated. Not changing the light."
