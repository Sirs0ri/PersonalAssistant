"""Handler for a Denon AVR-X1200W Audio/Video Receiver.

It reacts to various events triggered by my Chromecast, such as "App
(dis-)connected" or the type of media playing. Commands are sent via Telnet and
follow this documentation:
http://assets.denon.com/documentmaster/de/avr3313ci_protocol_v02.pdf
"""

###############################################################################
#
# TODO: [ ] get IP from config/router
#
###############################################################################


# standard library imports
import logging
import Queue
import socket
import telnetlib
import threading
import time
import traceback

# related third party imports

# application specific imports
# pylint: disable=import-error
from devices.device import BaseClass
from tools import SleeperThread
# pylint: enable=import-error


__version__ = "1.3.11"


# Initialize the logger
LOGGER = logging.getLogger(__name__)

COMM_QUEUE = Queue.PriorityQueue()


def send(command, device_ip, logger, retries=3):
    """Send a command to the connected AVR via Telnet."""
    if retries > 0:
        try:
            telnet = telnetlib.Telnet(device_ip)
            logger.debug("Sending command '%s'", command)
            telnet.write("{}\r".format(command))
            telnet.close()
        except socket.error:
            logger.exception("AVR refused the connection. Is another "
                             "device using the Telnet connection already?"
                             "\n%s", traceback.format_exc())
            time.sleep(2)
            send(command, device_ip, logger, retries-1)
    else:
        logger.error("Maximium count of retries reached. The command %s "
                     "couldn't be sent.", command)


def worker(device_ip):
    """Read and process commands from the COMM_QUEUE queue.

    Put results back into OUTPUT. This helps if 2 commands should be sent at
    the same time. Since the worker reads all items from a threadsafe Queue, no
    parallel processing (and thus no attempt to create a 2 telnet connections
    at the same time) is possible.
    """
    # Get a new logger for each thread.
    # Used instead of the global LOGGER on purpose inside this function.
    logger = logging.getLogger(
        __name__ + "." + threading.current_thread().name)

    while True:
        # Wait until an item becomes available in INPUT
        logger.debug("Waiting for a command.")
        command = COMM_QUEUE.get()
        send(command, device_ip, logger)
        COMM_QUEUE.task_done()


def turn_off_with_delay():
    """Turn the AVR off."""
    COMM_QUEUE.put("ZMOFF")


class Device(BaseClass):
    """The main class implementing the Audio/Video-Receiver."""

    def __init__(self, uid):
        """Initialize the device's hadler."""
        LOGGER.info("Initializing...")
        self.name = "AVR"
        self.uid = uid
        self.keywords = ["chromecast_playstate_change",
                         "chromecast_connection_change"]
        self.device_ip = "192.168.178.48"
        self.worker = threading.Thread(target=worker,
                                       args=(self.device_ip,),
                                       name="worker")
        self.worker.daemon = True
        self.worker.start()
        self.sleeper = None
        super(Device, self).__init__(logger=LOGGER, file_path=__file__)

    def stop(self):
        """Exit the device's hadler."""
        LOGGER.info("Exiting...")
        if self.sleeper:
            self.sleeper.join()
        COMM_QUEUE.join()
        return super(Device, self).stop()

    def process(self, key, data=None):
        """Process a command."""
        if key == "chromecast_connection_change":

            if self.sleeper is not None:
                # Stop the sleeper if it's already running
                LOGGER.debug("Stopping the sleeper-thread.")
                self.sleeper.stop()
                self.sleeper.join()
                self.sleeper = None

            # Check if the Chromecast is connected to an app
            if data["display_name"] in [None, "Backdrop"]:  # not connected
                LOGGER.debug("No app connected to the Chromecast.")
                # Run the sleeper that turns off the AVR after 3 minutes
                self.sleeper = SleeperThread(target=turn_off_with_delay,
                                             delay=120,
                                             name=__name__ + ".sleeper")
                self.sleeper.start()
                return True
            else:  # An app is connected to the Chromecast
                LOGGER.debug("'%s' connected to the Chromecast.",
                             data["display_name"])
                COMM_QUEUE.put("SIMPLAY")
                return True

        elif key == "chromecast_playstate_change":

            # Set the audio mode depending on what kind of content is playing
            if data["content_type"] is not None:
                command = ("MSSTEREO" if "audio" in data["content_type"] else
                           "MSDOLBY DIGITAL")
                # Prefer stereo audio for music, surround for everything else
                COMM_QUEUE.put(command)
                return True
        else:
            LOGGER.warn("Keyword not in use. (%s, %s)", key, data)
        return False
