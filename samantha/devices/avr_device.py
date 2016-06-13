"""Handler for a Denon AVR-X1200W Audio/Video Receiver. It reacts to various
events triggered by my Chromecast, such as "App (dis-)connected" or the type of
media playing. Commands are sent via Telnet and follow this documentation:
http://assets.denon.com/documentmaster/de/avr3313ci_protocol_v02.pdf"""

###############################################################################
#
# TODO: [ ] comments
# TODO: [ ] get IP from config/router
# TODO: [ ] use a Queue to make sure all commands are sent after each other
#
###############################################################################

import logging
import socket
import telnetlib
import threading
import time
import traceback

from devices.device import BaseClass


# Initialize the logger
LOGGER = logging.getLogger(__name__)


def turn_off_with_delay(self, delay=120):
    """Turns the AVR off after a delay of 120 seconds (default, can be changed
    via a parameter)"""

    logger = logging.getLogger(__name__ + ".sleeper")
    logger.debug("Started the sleeper-thread.")
    # Wait for a while, since this function is called as new Thread, it can
    # still be cancelled during this period.
    time.sleep(delay)
    try:
        tn = telnetlib.Telnet(self.ip)
        command = "ZMOFF"  # Turn the main zone off
        logger.debug("Sending command '%s'", command)
        tn.write("{}\r".format(command))
        tn.close()
    except socket.error:
        logger.exception("AVR refused the connection. Is another "
                         "device using the Telnet connection already?"
                         "\n%s", traceback.format_exc())


class Device(BaseClass):
    """The main class implementing the Device."""

    def __init__(self, uid):
        LOGGER.info("Initializing...")
        self.name = "AVR"
        self.uid = uid
        self.keywords = ["chromecast_playstate_change"]
        self.ip = "192.168.178.48"
        self.sleeper = None
        super(Device, self).__init__(logger=LOGGER, file_path=__file__)

    def process(self, key, data=None):
        """The main processing function. Ths will be called if an event's
        keyword matches one of the device's keywords (specified in __init__)"""

        if key == "chromecast_playstate_change":
            commands = []

            # Check if the Chromecast is connected to an app
            if data["media_session_id"] is None:  # not connected
                if self.sleeper is not None:
                    # Stop the sleeper if it's already running
                    LOGGER.debug("Stopping the sleeper-thread.")
                    self.sleeper.join(0)
                    self.sleeper = None

                # Run the sleeper that turns off the AVR after 3 minutes
                self.sleeper = threading.Thread(
                    target=turn_off_with_delay, args=(self,))
                self.sleeper.start()
            else:  # An app is connected to the Chromecast

                if self.sleeper is not None:
                    # Kill the sleeper if it's currently running
                    LOGGER.debug("Stopping the sleeper-thread.")
                    self.sleeper.join(0)
                    self.sleeper = None
                commands.append("SIMPLAY")


            # Set the audio mode depending on what kind of content is playing
            if data["content_type"] is not None:
                if "audio" in data["content_type"]:
                    # For audio, stereo sound is preferred
                    commands.append("MSSTEREO")
                else:
                    # This is the case for video (where surround sound is
                    # preferred) or pictures (where the sound doesn't matter)
                    commands.append("MSDOLBY DIGITAL")

            if commands:  # if any commands should be sent to the AVR
                try:
                    tn = telnetlib.Telnet(self.ip)
                    for command in commands:
                        LOGGER.debug("Sending command '%s'", command)
                        tn.write("{}\r".format(command))
                    tn.close()
                    return True
                except socket.error:
                    LOGGER.exception("AVR refused the connection. Is another "
                                     "device using the Telnet connection "
                                     "already?\n%s", traceback.format_exc())
            if self.sleeper is not None:
                return True
        else:
            LOGGER.warn("Keyword not in use. (%s, %s)", key, data)
        return False
