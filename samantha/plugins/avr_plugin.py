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
from core import subscribe_to
from plugins.plugin import Device


__version__ = "1.6.8"


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


def turn_off_with_delay(name="sleeper"):
    """Turn the AVR off."""
    logger = logging.getLogger(name)
    logger.debug("Sending the command to shut down the AVR.")
    COMM_QUEUE.put(["ZMOFF", ["SI?=SIMPLAY", True]])

WORKER = threading.Thread(target=worker, name="worker")
WORKER.daemon = True
SLEEPER = None

PLUGIN = Device("AVR", True, LOGGER, __file__)


@subscribe_to("system.onstart")
def onstart(key, data):
    """Set up the plugin by starting the worker-thread."""
    LOGGER.debug("Starting the worker")
    WORKER.start()
    return "Worker started successfully."


@subscribe_to("chromecast.connection_change")
def chromecast_connection_change(key, data):
    """React to a change of the Chromecast's connection."""
    global SLEEPER

    if SLEEPER is not None:
        # Stop the sleeper if it's already running
        LOGGER.debug("Stopping the sleeper-thread.")
        SLEEPER.cancel()
        SLEEPER.join()
        SLEEPER = None
        LOGGER.debug("Stopped the sleeper-thread.")


    # Check if the Chromecast is connected to an app
    if data["display_name"] in [None, "Backdrop"]:  # not connected
        LOGGER.debug("No app connected to the Chromecast. (%s)",
                     data["display_name"])
        # Run the sleeper that turns off the AVR after 3 minutes
        SLEEPER = threading.Timer(120.0,
                                  turn_off_with_delay,
                                  [__name__ + ".sleeper"])
        SLEEPER.start()
        LOGGER.debug("Started the Sleeper with a delay of 120 seconds.")
        return "Started the Sleeper."
    else:  # An app is connected to the Chromecast
        LOGGER.debug("'%s' connected to the Chromecast.",
                     data["display_name"])
        COMM_QUEUE.put(["ZMON", ["ZM?=ZMON", False]])
        COMM_QUEUE.put(["SIMPLAY", ["SI?=SIMPLAY", False]])
        return "Handled connecting of {} to the Chromecast.".format(
            data["display_name"])


@subscribe_to("chromecast.playstate_change")
def chromecast_playstate_change(key, data):
    """React to a change of the Chromecast's playstate."""

    # Set the audio mode depending on what kind of content is playing
    if data["content_type"] is not None:
        command = ("MSSTEREO" if "audio" in data["content_type"] else
                   "MSDOLBY DIGITAL")
        # Prefer stereo audio for music, surround for everything else
        condition = "MS?={}".format(command.split(" ")[0])
        COMM_QUEUE.put([command, [condition, False]])
        return "Set he audio mode to {}.".format(command)


@subscribe_to("system.onexit")
def stop(key, data):
    """Exit the device's hadler."""
    LOGGER.info("Exiting...")
    if SLEEPER:
        SLEEPER.cancel()
        SLEEPER.join()
    LOGGER.warn("Waiting for COMM_QUEUE to be emptied. It currently holds "
                "%d items.", COMM_QUEUE.qsize())
    COMM_QUEUE.join()
    LOGGER.info("Exited.")
    return "Exited."
