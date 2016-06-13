""""""

###############################################################################
#
# TODO: [ ] docstrings
# TODO: [ ] comments
# TODO: [ ] Read Chromecast IP from config
#
###############################################################################


import logging

import pychromecast

from devices.device import BaseClass
import tools

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
        updated = 0
        if not status.player_state == self.player_state:
            self.player_state = status.player_state
            LOGGER.debug("New state: %s", self.player_state)
            updated = 1
        if not status.content_type == self.content_type:
            self.content_type = status.content_type
            LOGGER.debug("New content_type: %s", self.content_type)
            updated = 1
        if updated:
            tools.eventbuilder.Event(sender_id=self.name,
                                     keyword="chromecast_playstate_change",
                                     data=status.__dict__).trigger()

    def new_cast_status(self, status):
        updated = 0
        if not status.display_name == self.display_name:
            self.display_name = status.display_name
            LOGGER.debug("New app connected: %s", self.display_name)
            updated = 1
        if updated:
            tools.eventbuilder.Event(sender_id=self.name,
                                     keyword="chromecast_connection_change",
                                     data=status.__dict__).trigger()


class Device(BaseClass):

    def __init__(self, uid):
        LOGGER.info("Initializing...")
        self.name = "Chromecast"
        self.uid = uid
        self.keywords = ["onstart"]

        self.cast = pychromecast.Chromecast("192.168.178.45")
        self.cast.wait()
        self.mc = self.cast.media_controller
        self.listener = Listener(self.name)
        self.mc.register_status_listener(self.listener)
        self.cast.register_status_listener(self.listener)
        super(Device, self).__init__(logger=LOGGER, file_path=__file__)

    def process(self, key, data=None):
        if key == "onstart":
            self.listener.new_media_status(self.mc.status)
            return True
        else:
            LOGGER.warn("Keyword not in use. (%s, %s)", key, data)
        return False
