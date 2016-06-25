""""""

###############################################################################
#
# TODO: [ ] docstrings
# TODO: [ ] comments
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


__version__ = "1.1.5"


# Initialize the logger
LOGGER = logging.getLogger(__name__)
logging.getLogger("pychromecast").setLevel(logging.INFO)


class Listener(object):

    def __init__(self, name):
        self.name = "{}_Listener".format(name)
        self.player_state = None
        self.content_type = None
        self.display_name = None

    def new_media_status(self, status):
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
        if not status.display_name == self.display_name:
            self.display_name = status.display_name
            LOGGER.debug("New app connected: %s", self.display_name)
        tools.eventbuilder.Event(sender_id=self.name,
                                 keyword="chromecast_connection_change",
                                 data=status.__dict__).trigger()


class Device(BaseClass):

    def __init__(self, uid):
        LOGGER.info("Initializing...")
        self.name = "Chromecast"
        self.uid = uid
        self.keywords = ["onstart"]

        try:
            self.cast = pychromecast.Chromecast("192.168.178.45")
            self.cast.wait()
            self.mc = self.cast.media_controller
            self.listener = Listener(self.name)
            self.mc.register_status_listener(self.listener)
            self.cast.register_status_listener(self.listener)
            active = True
        except Exception:
            self.cast = None
            active = False
            LOGGER.exception("Exception while connecting to the Chromecast:\n%s",
                             traceback.format_exc())
        finally:
            super(Device, self).__init__(logger=LOGGER,
                                         file_path=__file__,
                                         active=active)

    def process(self, key, data=None):
        if key == "onstart" and self.cast:
            self.listener.new_media_status(self.mc.status)
            self.listener.new_cast_status(self.cast.status)
            return True
        else:
            LOGGER.warn("Keyword not in use. (%s, %s)", key, data)
        return False
