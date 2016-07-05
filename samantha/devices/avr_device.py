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
from collections import Iterable
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
from core import subscribe_to
from devices.device import BaseClass
from tools import SleeperThread
# pylint: enable=import-error


__version__ = "1.5.6"


# Initialize the logger
LOGGER = logging.getLogger(__name__)

COMM_QUEUE = Queue.PriorityQueue()


def _check_condition(condition, telnet, logger):
    """Check if the given condition is met.

    Is must be in the format ["COMMAND=RESULT", Boolean]. Depending on the
    boolean, the condition is met when the result is part of the command's
    result (Bool == True) or not (Bool == False).
    """
    if condition is None:
        return True
    try:
        condition_must_match = condition[1]
        cond_comm, cond_val = condition[0].split("=")

        telnet.read_very_eager()  # Clear the device's output

        # Send the command specified in the condition
        telnet.write("{}\r".format(cond_comm))

        output = telnet.read_some()  # Read the output
        output = output.replace("\r", " ")
        logger.debug("Condition was: '%s'. Output was: '%s'",
                     condition, output)

        if condition_must_match == (cond_val in output):
            return True

    except ValueError:
        logger.exception("Error while procesing the condition '%s'.",
                         condition)

    return False


def _send(command, device_ip, logger, condition=None, retries=3):
    """Send a command to the connected AVR via Telnet."""
    if retries > 0:
        telnet = None
        while retries > 0:
            try:
                telnet = telnetlib.Telnet(device_ip)
                break
            except socket.error:
                logger.warn("AVR refused the connection. Retrying...")
                retries -= 1
                time.sleep(1)
        if telnet is None:
            logger.exception("AVR refused the connection. Is another "
                             "device using the Telnet connection already?"
                             "\n%s", traceback.format_exc())
        else:
            if not _check_condition(condition, telnet, logger):
                logger.debug("Not sending the command because the condition "
                             "'%s' is not fulfilled.", condition)
            else:
                logger.debug("Sending command '%s'", command)
                telnet.write("{}\r".format(command))
                logger.debug("Successfully sent the command '%s'.", command)

            # Close the telnet connection in any case
            telnet.close()

    else:
        logger.error("Maximium count of retries reached. The command '%s' "
                     "couldn't be sent.", command)


def worker(device_ip="192.168.178.48"):
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
        if not isinstance(command, str) and isinstance(command, Iterable):
            _send(command[0], device_ip, logger, command[1])
        else:
            _send(command, device_ip, logger)
        COMM_QUEUE.task_done()


def turn_off_with_delay():
    """Turn the AVR off."""
    LOGGER.debug("Sending the command to shut down the AVR.")
    COMM_QUEUE.put(["ZMOFF", ["SI?=SIMPLAY", True]])

SLEEPER = None
WORKER = None

DEVICE = BaseClass("AVR", True, LOGGER, __file__)


@subscribe_to("onstart")
def onstart(key, data):
    global WORKER
    LOGGER.debug("Starting the worker")
    device_ip = "192.168.178.48"
    WORKER = threading.Thread(target=worker, name="worker")
    WORKER.daemon = True
    WORKER.start()
    return True


@subscribe_to("chromecast_connection_change")
def chromecast_connection_change(key, data):
    global SLEEPER

    if SLEEPER is not None:
        # Stop the sleeper if it's already running
        LOGGER.debug("Stopping the sleeper-thread.")
        SLEEPER.stop()
        SLEEPER.join()
        SLEEPER = None

    # Check if the Chromecast is connected to an app
    if data["display_name"] in [None, "Backdrop"]:  # not connected
        LOGGER.debug("No app connected to the Chromecast.")
        # Run the sleeper that turns off the AVR after 3 minutes
        SLEEPER = SleeperThread(target=turn_off_with_delay,
                                delay=120,
                                name=__name__ + ".sleeper")
        SLEEPER.start()
        return True
    else:  # An app is connected to the Chromecast
        LOGGER.debug("'%s' connected to the Chromecast.",
                     data["display_name"])
        COMM_QUEUE.put(["ZMON", ["ZM?=ZMON", False]])
        COMM_QUEUE.put(["SIMPLAY", ["SI?=SIMPLAY", False]])
        return True


@subscribe_to("test")
def test(key, data):
    global SLEEPER

    if SLEEPER is not None:
        # Stop the sleeper if it's already running
        LOGGER.debug("Stopping the sleeper-thread.")
        SLEEPER.stop()
        SLEEPER.join()
        SLEEPER = None

    SLEEPER = SleeperThread(target=turn_off_with_delay,
                            delay=5,
                            name=__name__ + ".sleeper")
    SLEEPER.start()
    return True


@subscribe_to("chromecast_playstate_change")
def chromecast_playstate_change(key, data):

    # Set the audio mode depending on what kind of content is playing
    if data["content_type"] is not None:
        command = ("MSSTEREO" if "audio" in data["content_type"] else
                   "MSDOLBY DIGITAL")
        # Prefer stereo audio for music, surround for everything else
        condition = "MS?={}".format(command.split(" ")[0])
        COMM_QUEUE.put([command, [condition, False]])
        return True


@subscribe_to("onexit")
def stop(key, data):
    """Exit the device's hadler."""
    LOGGER.info("Exiting...")
    if SLEEPER:
        SLEEPER.stop()
        SLEEPER.join()
    COMM_QUEUE.join()
