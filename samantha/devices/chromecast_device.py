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
from devices.device import BaseClass
import tools
# pylint: enable=import-error


__version__ = "1.1.10"


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
                                 keyword="chromecast_playstate_change",
                                 data=status.__dict__).trigger()

    def new_cast_status(self, status):
        """React to the "new_cast_status" event."""
        if not status.display_name == self.display_name:
            self.display_name = status.display_name
            LOGGER.debug("New app connected: %s", self.display_name)
        tools.eventbuilder.Event(sender_id=self.name,
                                 keyword="chromecast_connection_change",
                                 data=status.__dict__).trigger()


class Device(BaseClass):
    """Implement methods to monitor a Chromecats's status."""

    def __init__(self, uid):
        """Initialize this device."""
        LOGGER.info("Initializing...")
        self.name = "Chromecast"
        self.uid = uid
        self.keywords = ["onstart"]

        try:
            # Connect to the Chromecast
            self.cast = pychromecast.Chromecast("192.168.178.45")
            self.cast.wait()  # Wait until the connection is ready.
            self.mediacontroller = self.cast.media_controller
            self.listener = Listener(self.name)
            # Register the listener to the Chromecast's status and media-status
            # events.
            self.mediacontroller.register_status_listener(self.listener)
            self.cast.register_status_listener(self.listener)
            active = True
        except Exception:
            self.cast = None
            active = False
            # This will mark the device as inactive later so that it's not
            # being forwarded any commands.
            LOGGER.exception(
                "Exception while connecting to the Chromecast:\n%s",
                traceback.format_exc())
        finally:
            super(Device, self).__init__(logger=LOGGER,
                                         file_path=__file__,
                                         active=active)

    def process(self, key, data=None):
        """Process a command from the core."""
        if key == "onstart" and self.cast:
            self.listener.new_media_status(self.mediacontroller.status)
            self.listener.new_cast_status(self.cast.status)
            return True
        else:
            LOGGER.warn("Keyword not in use. (%s, %s)", key, data)
        return False

    def stop(self):
        """Exit the device-handler.

        I would un-register the listeners here, but the library pxchromecast
        doesn't support it yet.
        """
        return super(Device, self).stop()
