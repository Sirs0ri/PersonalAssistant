"""This handler connects and represents my ChromeCast.

It fires events when the playback and the connection changes.
"""

###############################################################################
#
# TODO: [ ] Read Chromecast IP from config
# TODO: [ ] Move adding the listeners to the initialisation, catch this:
#               Traceback (most recent call last):
#                 File "samantha/plugins/chromecast_plugin.py", line 79, in onstart
#                   cast = pychromecast.Chromecast("192.168.178.45")
#                 File "/usr/local/lib/python2.7/dist-packages/pychromecast/__init__.py", line 244, in __init__
#                   "Could not connect to {}:{}".format(self.host, self.port))
#               ChromecastConnectionError: Could not connect to 192.168.178.45:8009
#               Exception AttributeError: "'Chromecast' object has no attribute 'socket_client'" in <bound method Chromecast.__del__ of Chromecast('192.168.178.45', port=8009, device=None)> ignored
#
###############################################################################


# standard library imports
import logging
import traceback

# related third party imports
import pychromecast

# application specific imports
from core import subscribe_to
from plugins.plugin import Plugin
from tools import eventbuilder


__version__ = "1.3.5"


# Initialize the logger
LOGGER = logging.getLogger(__name__)
logging.getLogger("pychromecast").setLevel(logging.INFO)


PLUGIN = Plugin("Chromecast", True, LOGGER, __file__)


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
            eventbuilder.Event(sender_id=self.name,
                               keyword="chromecast.playstate_change",
                               data=status.__dict__).trigger()

    def new_cast_status(self, status):
        """React to the "new_cast_status" event."""
        if status.display_name:
            # Skip the event if the displayed name is None. That happens
            # sometimes for a short moment if a new app connects.
            if not status.display_name == self.display_name:
                self.display_name = status.display_name
                LOGGER.debug("New app connected: %s", self.display_name)
                eventbuilder.Event(sender_id=self.name,
                                   keyword="chromecast.connection_change",
                                   data=status.__dict__).trigger()


@subscribe_to("system.onstart")
def onstart(key, data):
    """Set up the Chromecast listener."""
    try:
        # Connect to the Chromecast
        cast = pychromecast.Chromecast("192.168.178.45")
        cast.wait()  # Wait until the connection is ready.
        mediacontroller = cast.media_controller
        listener = Listener(PLUGIN.name)
        # Register the listener to the Chromecast's status and media-status
        # events.
        mediacontroller.register_status_listener(listener)
        cast.register_status_listener(listener)
        listener.new_media_status(mediacontroller.status)
        listener.new_cast_status(cast.status)
        return "Registered both Listeners successfully."
    except Exception, e:
        LOGGER.exception(
            "Exception while connecting to the Chromecast:\n%s",
            traceback.format_exc())
    return "Error: {}".format(e)
