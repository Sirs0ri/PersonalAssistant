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
import traceback

# related third party imports
import pychromecast

# application specific imports
# pylint: disable=import-error
from core import subscribe_to
from devices.device import BaseClass
import tools
# pylint: enable=import-error


__version__ = "1.2.5"


# Initialize the logger
LOGGER = logging.getLogger(__name__)
logging.getLogger("pychromecast").setLevel(logging.INFO)


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
        if not status.content_type == self.content_type:
            self.content_type = status.content_type
            LOGGER.debug("New content_type: %s", self.content_type)
        tools.eventbuilder.Event(sender_id=self.name,
                                 keyword="chromecast.playstate_change",
                                 data=status.__dict__).trigger()

    def new_cast_status(self, status):
        """React to the "new_cast_status" event."""
        if not status.display_name == self.display_name:
            self.display_name = status.display_name
            LOGGER.debug("New app connected: %s", self.display_name)
        tools.eventbuilder.Event(sender_id=self.name,
                                 keyword="chromecast.connection_change",
                                 data=status.__dict__).trigger()


DEVICE = BaseClass("Chromecast", True, LOGGER, __file__)


@subscribe_to("system.onstart")
def onstart(key, data):
    """Set up the Chromecast listener."""
    try:
        # Connect to the Chromecast
        cast = pychromecast.Chromecast("192.168.178.45")
        cast.wait()  # Wait until the connection is ready.
        mediacontroller = cast.media_controller
        listener = Listener(DEVICE.name)
        # Register the listener to the Chromecast's status and media-status
        # events.
        mediacontroller.register_status_listener(listener)
        cast.register_status_listener(listener)
        listener.new_media_status(mediacontroller.status)
        listener.new_cast_status(cast.status)
        return True
    except Exception:
        LOGGER.exception(
            "Exception while connecting to the Chromecast:\n%s",
            traceback.format_exc())
    return False
