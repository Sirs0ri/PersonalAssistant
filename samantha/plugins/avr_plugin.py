"""Handler for a Denon AVR-X1200W Audio/Video Receiver.

It reacts to various events triggered by my Chromecast, such as "App
(dis-)connected" or the type of media playing. Commands are sent via Telnet and
follow this documentation:
http://assets.denon.com/documentmaster/de/avr3313ci_protocol_v02.pdf
"""

###############################################################################
#
# TODO: [ ] get IP from config/router
# TODO: [X] build commands from base class:
#   DO, WHILE_DO, IF_DO
#   com.execute(), depending on ^^^
# TODO: [ ] Test old commands:
# TODO: [ ]     turn_off_with_delay
# TODO: [ ]     chromecast_connection_change
# TODO: [ ]     chromecast_playstate_change
# TODO: [X] Docstrings
# TODO: [X] Mute ("SIMUON/OFF/?")
# TODO: [ ] profile.night command
# TODO: [WIP] Improve performance while sending commands
#
###############################################################################


# standard library imports
# from collections import Iterable
from enum import Enum
import logging
import queue
import re
import socket
import telnetlib
import threading
import time
import traceback

# related third party imports

# application specific imports
from samantha.core import subscribe_to
from samantha.plugins.plugin import Device


__version__ = "1.7a2"


# Initialize the logger
LOGGER = logging.getLogger(__name__)

COMM_QUEUE = queue.Queue()

DEVICE_IP = "192.168.178.48"

try:
    telnet = telnetlib.Telnet(DEVICE_IP)
    telnet.close()
    ACTIVE = True
except socket.error:
    ACTIVE = False


class CommandType(Enum):
    DO = 1
    WHILE_DO = 2
    IF_DO = 3


class TelnetConnection:
    def __init__(self, retries=3):
        """Connection to the AVR. Used as parent for Command and Condition.

        :param retries:  Number of max. retries. (default: 3)
        """
        self.connection_retries = retries
        self._telnet = None
        
    def _connect(self):
        """Connect to the AVR.

        :return: True, if the connection succeeded, False otherwise.
        """
        self._telnet = None
        while self.connection_retries > 0:
            # Try establishing a telnet connection
            try:
                self._telnet = telnetlib.Telnet(DEVICE_IP)
                return True  # Connection successful
            except socket.error:
                LOGGER.warning("AVR refused the connection. Retrying...")
                self.connection_retries -= 1
                time.sleep(1)
        if self._telnet is None:
            LOGGER.error("AVR refused the connection. Is another "
                         "device using the Telnet connection already?"
                         "\n%s", traceback.format_exc())
            return False
    
    def _disconnect(self):
        """Disconnect the Telnet connection to the AVR."""
        if self._telnet:
            self._telnet.close()
            
    def _execute_command(self, command):
        """Send a command to the connected AVR via Telnet.
        :param command: The command to be executed
        :return: The command's output
        """
        LOGGER.debug("Sending command '%s'", command)
        self._telnet.write("{}\r".format(command).encode("utf-8"))
        LOGGER.debug("Successfully sent the command '%s'.", command)
        output = self._telnet.read_some()  # Read the output
        output = output.decode("utf-8").replace("\r", " ")
        return output.strip()
        

class Condition(TelnetConnection):
    def __init__(self, command=None, expectation=None,
                 must_match=True, retries=3):
        """Initialize the condition.
        
        If command is None, this will return ecpectation.

        :param command: Command to produce the output that is to be checked.
        :param expectation: The expected output.
        :param must_match: Whether the output must match the expectation. This
        parameter allows for "EQUAL" and "NOT EQUAL" comparison
        :param retries:  Number of max. retries. (default: 3)
        :return: Boolean, whether the condition checks out or not.
        """
        super().__init__(retries)
        self.command = command
        self.expectation = expectation
        self.must_match = must_match
    
    def check(self):
        if not self.command:
            return self.expectation
        else:
            result = self._execute_command(self.command)
            matches = result == self.expectation
            LOGGER.debug("Condition was: '%s'. Comparing to: '%s'. "
                         "Matches: %s. Should match: %s.",
                         self.expectation, result,
                         matches, self.must_match)
            return matches == self.must_match


class Command(TelnetConnection):
    def __init__(self, command, command_type=CommandType.DO,
                 condition=Condition(expectation=True), retries=3):
        """Initialize the command.

        :param command: Command to be sent to the AVR
        :param command_type: Type of the command (default: CommandType.DO)
        :param condition: Condition to execute the command (default: None)
        :param retries: Number of max. retries. (default: 3)
        """
        super().__init__(retries)
        self.command = command
        self.type = command_type
        self.condition = condition

    def execute(self):
        """Execute self.command."""
        if self._connect():
            while self.condition.check():
                self._execute_command(self.command)
                if self.type is not CommandType.WHILE_DO:
                    break
        else:
            LOGGER.error("Couldn't send the command %s since the SVR refused "
                         "to connect.", self.command)
        self._disconnect()  # Disconnect either way


class SmoothVolumeCommand(Command):
    def __init__(self, target_volume,
                 condition=Condition(expectation=True), retries=3):
        """Initialize the command.

        :param target_volume: The value to adjust the volume to
        :param retries: Number of max. retries. (defaul: 3)
        """
        target_volume = int(target_volume)
        self.target_volume = (0 if target_volume < 0 else
                              98 if target_volume > 98 else
                              target_volume)
        self.vol_condition = condition
        while_condition = Condition("MV?",
                                    "MV{}".format(self.target_volume),
                                    False)
        super().__init__(None, CommandType.WHILE_DO, while_condition, retries)
        
    def _parse(self, result):
        """ Parse the current volume and adjust self.command.

        :param result: output of MV?, eg. MV125 for 12.5
        """
        match = re.match(r"MV(?P<vol>\d{2})(?P<dec>\d?)", result)
        if int(match.group("vol")) < self.target_volume:
            self.command = "MVUP"
        else:
            self.command = "MVDOWN"
   
    def execute(self):
        """Parse current volume, then execute via parent function."""
        self._parse(self._execute_command("MV?"))
        if self.vol_condition.check():
            super().execute()


# def _check_condition(condition, _telnet, logger):
#     """Check if the given condition is met.
#
#     Is must be in the format ["COMMAND=RESULT", Boolean]. Depending on the
#     boolean, the condition is met when the result is part of the command's
#     result (Bool == True) or not (Bool == False).
#     """
#     if condition is None:
#         return True
#     try:
#         condition_must_match = condition[1]
#         cond_comm, cond_val = condition[0].split("=")
#
#         _telnet.read_very_eager()  # Clear the device's output
#
#         # Send the command specified in the condition
#         _telnet.write("{}\r".format(cond_comm).encode("utf-8"))
#
#         output = _telnet.read_some()  # Read the output
#         output = output.decode("utf-8").replace("\r", " ")
#         logger.debug("Condition was: '%s'. Output was: '%s'",
#                      condition, output)
#
#         if condition_must_match == (cond_val in output):
#             return True
#
#     except ValueError:
#         logger.exception("Error while processing the condition '%s'.",
#                          condition)
#
#     return False
#
#
# def _send(command, logger, condition=None, retries=3):
#     """Send a command to the connected AVR via Telnet."""
#     if retries > 0:
#         _telnet = None
#         while retries > 0:
#             try:
#                 _telnet = telnetlib.Telnet(DEVICE_IP)
#                 break
#             except socket.error:
#                 logger.warning("AVR refused the connection. Retrying...")
#                 retries -= 1
#                 time.sleep(1)
#         if _telnet is None:
#             logger.error("AVR refused the connection. Is another "
#                          "device using the Telnet connection already?"
#                          "\n%s", traceback.format_exc())
#         else:
#             if not _check_condition(condition, _telnet, logger):
#                 logger.debug("Not sending the command because the condition "
#                              "'%s' is not fulfilled.", condition)
#             else:
#                 logger.debug("Sending command '%s'", command)
#                 _telnet.write("{}\r".format(command).encode("utf-8"))
#                 logger.debug("Successfully sent the command '%s'.", command)
#
#             # Close the telnet connection in any case
#             _telnet.close()
#
#     else:
#         logger.error("Maximium count of retries reached. The command '%s' "
#                      "couldn't be sent.", command)


def worker():
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
        logger.warning("Processing command %s", command)
        command.execute()
        COMM_QUEUE.task_done()


def turn_off_with_delay(name="sleeper"):
    """Turn the AVR off."""
    logger = logging.getLogger(name)
    logger.debug("Sending the command to shut down the AVR.")
    condition = Condition("SI?", "SIMPLAY", True)
    command = Command(command="ZMOFF", condition=condition)
    COMM_QUEUE.put(command)

WORKER = threading.Thread(target=worker, name="worker")
WORKER.daemon = True
SLEEPER = None

PLUGIN = Device("AVR", ACTIVE, LOGGER, __file__)


@subscribe_to("system.onstart")
def onstart(key, data):
    """Set up the plugin by starting the worker-thread."""
    LOGGER.debug("Starting the worker")
    WORKER.start()
    return "Worker started successfully."


@subscribe_to("set.avr.volume")
def set_vol(key, data):
    if "volume" in data:
        command = SmoothVolumeCommand(data["volume"])
        COMM_QUEUE.put(command)
        return "Volume adjusted successfully to {}.".format(data["volume"])
    return "Parameter 'volume' is missing."


@subscribe_to("set.avr.mute")
def set_vol(key, data):
    if "mute" in data:
        if bool(data["mute"]):
            command = Command("SIMUON")
            status = "on"
        else:
            command = Command("SIMUOFF")
            status = "off"
        COMM_QUEUE.put(command)
        return "Mute turned {} successfully.".format(status)
    return "Parameter 'mute' is missing."
    

@subscribe_to("set.avr.sleep")
def set_sleep(key, data):
    if "sleep" in data:
        duration = int(data["sleep"])
        if duration < 1:
            command = Command("SLPOFF")
            result = "Sleep timer turned off successfully."
        else:
            if duration > 120:
                duration = 120
            command = Command("SLP{0:03d}".format(duration))
            result = "Sleep timer adjusted successfully to {} minutes.".format(
                duration)
        COMM_QUEUE.put(command)
    else:
        result = "Parameter 'sleep' is missing."
    return result
    

@subscribe_to("profile.active.night")
def activate_night_profile(key, data):
    """Reduce volume and turn on 20 minute timer if device is on."""
    condition = Condition("PW?", "PWON")
    command_vol = SmoothVolumeCommand(13, condition=condition)
    command_mute = Command("SIMUON", condition=condition)
    command_timer = Command("SLP20", condition=condition)
    COMM_QUEUE.put(command_vol)
    COMM_QUEUE.put(command_mute)
    COMM_QUEUE.put(command_timer)
    return "Adjusted volume, mute and timer"
    

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
        # Run the sleeper that turns off the AVR after 2 minutes
        SLEEPER = threading.Timer(120.0,
                                  turn_off_with_delay,
                                  [__name__ + ".sleeper"])
        SLEEPER.start()
        LOGGER.debug("Started the Sleeper with a delay of 120 seconds.")
        return "No app connected, Started the Sleeper."
    else:  # An app is connected to the Chromecast
        LOGGER.debug("'%s' connected to the Chromecast.",
                     data["display_name"])
        condition_is_off = Condition("ZM?", "ZMON", False)
        command_on = Command("ZMON", condition=condition_is_off)
        COMM_QUEUE.put(command_on)
        condition_input_not_play = Condition("SI?", "SIMPLAY", False)
        command_switch_input_play = Command("SIMPLAY",
                                            condition=condition_input_not_play)
        COMM_QUEUE.put(command_switch_input_play)
        return "Handled connecting of {} to the Chromecast.".format(
            data["display_name"])


@subscribe_to("chromecast.contenttype_change")
def chromecast_playstate_change(key, data):
    """React to a change of the Chromecast's playstate."""

    # Set the audio mode depending on what kind of content is playing
    if data["content_type"] is not None:
        comm_text = ("MSSTEREO" if "audio" in data["content_type"] else
                     "MSDOLBY DIGITAL")
        # Prefer stereo audio for music, surround for everything else
        condition = Condition("MS?", comm_text.split(" ")[0])
        command = Command(comm_text, condition=condition)
        COMM_QUEUE.put(command)
        return "Set he audio mode to {}.".format(comm_text)
    else:
        return "Invalid content-type. Looks like no app is currently connected."


@subscribe_to("system.onexit")
def stop(key, data):
    """Exit the device's handler."""
    LOGGER.info("Exiting...")
    if SLEEPER:
        SLEEPER.cancel()
        SLEEPER.join()
    LOGGER.warning("Waiting for COMM_QUEUE to be emptied. It currently holds "
                   "%d items.", COMM_QUEUE.qsize())
    COMM_QUEUE.join()
    LOGGER.info("Exited.")
    return "Exited."
