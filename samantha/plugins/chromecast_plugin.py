"""This handler connects and represents my ChromeCast.

It fires events when the playback and the connection changes.
"""

###############################################################################
#
# TODO: [ ] Read Chromecast IP from config
#
###############################################################################


# standard library imports
import logging

# related third party imports
import pychromecast

# application specific imports
from samantha.core import subscribe_to
from samantha.plugins.plugin import Plugin
from samantha.tools import eventbuilder


__version__ = "1.3.10"


# Initialize the logger
LOGGER = logging.getLogger(__name__)
logging.getLogger("pychromecast").setLevel(logging.INFO)

try:
    # Connect to the Chromecast
    CAST = pychromecast.Chromecast("192.168.178.45")
    CAST.wait()  # Wait until the connection is ready.
except pychromecast.ChromecastConnectionError:
    CAST = None


PLUGIN = Plugin("Chromecast", CAST is not None, LOGGER, __file__)


class Listener(object):
    """Listen to state-changes from the chromecast."""

    def __init__(self, name):
        """Set up the listener."""
        self.name = "{}_Listener".format(name)
        self.player_state = None
        self.content_type = None
        self.display_name = None

    def new_media_status(self, status):
        """React to the "new_media_status" event."""
        if not status.player_state == self.player_state:
            self.player_state = status.player_state
            LOGGER.debug("New state: %s", self.player_state)
            eventbuilder.eEvent(sender_id=self.name,
                                keyword="chromecast.playstate_change",
                                data=status.__dict__).trigger()
        if not status.content_type == self.content_type:
            self.content_type = status.content_type
            LOGGER.debug("New content_type: %s", self.content_type)
            eventbuilder.eEvent(sender_id=self.name,
                                keyword="chromecast.contenttype_change",
                                data=status.__dict__).trigger()

    def new_cast_status(self, status):
        """React to the "new_cast_status" event."""
        if status.display_name:
            # Skip the event if the displayed name is None. That happens
            # sometimes for a short moment if a new app connects.
            if not status.display_name == self.display_name:
                self.display_name = status.display_name
                LOGGER.debug("New app connected: %s", self.display_name)
                eventbuilder.eEvent(sender_id=self.name,
                                    keyword="chromecast.connection_change",
                                    data=status.__dict__).trigger()


@subscribe_to("system.onstart")
def onstart(key, data):
    """Set up the Chromecast listener."""
    try:
        mediacontroller = CAST.media_controller
        listener = Listener(PLUGIN.name)
        # Register the listener to the Chromecast's status and media-status
        # events.
        mediacontroller.register_status_listener(listener)
        CAST.register_status_listener(listener)
        listener.new_media_status(mediacontroller.status)
        listener.new_cast_status(CAST.status)
        return "Registered both Listeners successfully."
    except pychromecast.ChromecastConnectionError, e:
        LOGGER.error("Could not connect to the ChromeCast. Error: %s", e)
        return "Error: {}".format(e)
