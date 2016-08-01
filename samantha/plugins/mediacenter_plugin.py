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
import context
from core import subscribe_to
from tools import eventbuilder
from plugins.plugin import Plugin


__version__ = "1.0.3"

# Initialize the logger
LOGGER = logging.getLogger(__name__)

PLUGIN = Plugin("Mediacenter", True, LOGGER, __file__)


@subscribe_to("chromecast.connection_change")
def chromecast_connection_change(key, data):
    """React to a change of the Chromecast's connection."""
    # Check if the Chromecast is connected to an app
    if context.get_value("time.time_of_day") == "night":
        if data["display_name"] in [None, "Backdrop"]:  # not connected
            eventbuilder.Event(sender_id=PLUGIN.name,
                               keyword="turn.off.ambient.433").trigger()
            eventbuilder.Event(sender_id=PLUGIN.name,
                               keyword="turn.on.led").trigger()
            return "Ambient light turned off."
        else:  # An app is connected to the Chromecast
            eventbuilder.Event(sender_id=PLUGIN.name,
                               keyword="turn.on.ambient.light").trigger()
            return "Ambient light turned on."
    return "It's daytime. The light is supposed to stay off."
