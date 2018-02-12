"""A plugin to test loading devices. It doesn't do anything."""

###############################################################################
#
# TODO: [ ]
#
###############################################################################


# standard library imports
import datetime
import logging
import threading
import time

# related third party imports
import flux_led

# application specific imports
from samantha.core import subscribe_to
from samantha.plugins.plugin import Device, Plugin


__version__ = "1.0.0a1"

# Initialize the logger
LOGGER = logging.getLogger(__name__)

SYNC_STEPS = []


def _fill_sync_steps():
    global SYNC_STEPS

    r = 255
    g = 0
    b = 0

    SYNC_STEPS = []
    temp_list = []

    for i in range(0, 255, 1):
        g = i
        temp_list.append((r, g, b))
    for i in range(255, 0, -1):
        r = i
        temp_list.append((r, g, b))
    for i in range(0, 255, 1):
        b = i
        temp_list.append((r, g, b))
    for i in range(255, 0, -1):
        g = i
        temp_list.append((r, g, b))
    for i in range(0, 255, 1):
        r = i
        temp_list.append((r, g, b))
    for i in range(255, 0, -1):
        b = i
        temp_list.append((r, g, b))

    SYNC_STEPS = temp_list


class MyWifiLed(flux_led.WifiLedBulb):

    def __init__(self, ipaddr, port=5577, timeout=5):
        super().__init__(ipaddr, port, timeout)
        self.NEW_COMMAND = threading.Event()
        self.IDLE = threading.Event()
        self.IDLE.set()

    def stop_previous_command(self):
        """Stop the currently executed command.

        While some functions here "do their thing" and then are done, some may run
        in an endless loop (like the fade- or strobe-functions. This method makes
        sure that the currently executed command is stopped before another one is
        executed.
        """
        self.NEW_COMMAND.set()
        self.IDLE.wait()
        self.NEW_COMMAND.clear()
        self.IDLE.clear()

    def fade(self):
        def fadesync_worker(start_at=0):
            current_step = start_at
            self.update_state()
            last_state = self.raw_state
            while not self.NEW_COMMAND.is_set():
                self.update_state()
                current_state = self.raw_state
                if current_state != last_state:
                    LOGGER.debug("State changed externally! Stopping the fade.")
                    break
                dt = datetime.datetime.utcnow().timestamp()
                next_step = int(dt * 5)  # new step every every .2 seconds
                if next_step > current_step:
                    current_step = next_step % len(SYNC_STEPS)
                    r, g, b = SYNC_STEPS[current_step]
                    self.setRgb(r, g, b)
                    self.update_state()
                    last_state = self.raw_state
                time.sleep(0.05)
            self.IDLE.set()
            print("done")

        self.stop_previous_command()

        if not SYNC_STEPS:
            _fill_sync_steps()

        # Get the step in the list to start with, for 1 sec in the future
        timestamp_now = datetime.datetime.utcnow().timestamp()
        timestamp_start = int((timestamp_now + 1) * 5)
        step_start = timestamp_start % len(SYNC_STEPS)
        r, g, b = SYNC_STEPS[step_start]
        self.setRgb(r, g, b)

        t = threading.Thread(target=fadesync_worker,
                             kwargs={"start_at": timestamp_start})
        t.start()

        return "The LEDs are now fading synchronized."


PLUGIN = Plugin("MagicHome", True, LOGGER, __file__)

desk_active = False
try:
    desk_led = MyWifiLed('192.168.178.103')
    desk_active = True
finally:
    DESK_LED = Device("DeskLED", desk_active, LOGGER, __file__, ["light", "magichome"])


@subscribe_to("desk.fade")
def fade(key, data):
    desk_led.turnOn()
    return desk_led.fade()


@DESK_LED.turn_on
def desk_turn_on(key, data):
    """Turn on the Reading-Lamp."""
    desk_led.turnOn()
    desk_led.setRgb(255, 85, 17)
    return "Desk turned on."


# @subscribe_to("system.onstart")
# def start_func(key, data):
#     """Test the 'onstart' event."""
#     LOGGER.debug("I'm now doing something productive!")
#     return "I'm now doing something productive!"


@DESK_LED.turn_off
def rl_turn_off(key, data):
    """Turn off the Reading-Lamp."""
    desk_led.turnOff()
    return "Desk turned off."


@subscribe_to("system.onexit")
def stop_func(key, data):
    """Test the 'onexit' event."""
    desk_led.stop_previous_command()
    LOGGER.debug("I'm not doing anything productive anymore.")
    return "I'm not doing anything productive anymore."
