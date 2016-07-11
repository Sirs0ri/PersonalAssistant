"""A device to test loading devices. It doesn't do anything."""

###############################################################################
#
# TODO: [ ]
#
###############################################################################


# standard library imports
import logging

# related third party imports
try:
    import pigpio
except ImportError:
    pigpio = None

# application specific imports
# pylint: disable=import-error
from core import subscribe_to
from devices.device import BaseClass
# pylint: enable=import-error


__version__ = "1.0.0"


# Initialize the logger
LOGGER = logging.getLogger(__name__)

if pigpio:
    PI = pigpio.pi("192.168.178.56")
else:
    LOGGER.exception(
        "Could not import pigpio. Please follow the instructions on %s to "
        "install it manually.",
        "https://github.com/joan2937/pigpio/blob/master/README#L103")

if PI.connected:
    RED_PINS = [12, 25]
    GREEN_PINS = [20, 23]
    BLUE_PINS = [21, 18]
else:
    LOGGER.error("Could not connect to the RasPi at 192.168.178.56.")

DEVICE = BaseClass("LED", PI.connected, LOGGER, __file__)


def _set_pins(red=-1, green=-1, blue=-1):
    if 0 <= red <= 255:
        for pin in RED_PINS:
            PI.set_PWM_dutycycle(pin, red)
    if 0 <= green <= 255:
        for pin in GREEN_PINS:
            PI.set_PWM_dutycycle(pin, green)
    if 0 <= blue <= 255:
        for pin in BLUE_PINS:
            PI.set_PWM_dutycycle(pin, blue)


def _spread(steps, length=255):
    """Spread an amount of 'steps' evenly in a list with 'length' items."""
    # Convert the args to floats
    length = float(length)
    steps = float(steps)
    # Create a 'length' long list with evenly distributed items [0 ... 'steps']
    result = [round(x*(steps/length)) for x in range(1, int(length)+1)]
    # For each item, set the item to it's rounded difference to the item before
    val = 0.0
    for i, value in enumerate(result):
        result[i], val = int(value - val), value
    return result


def _crossfade(red=-1, green=-1, blue=-1, speed=1.0):
    steps = int(256 * speed)
    if 0 <= red <= 255:
        red_is = PI.get_PWM_dutycycle(RED_PINS[0])
        red_diff = red - red_is
        red_list = _spread(red_diff, steps)
    if 0 <= green <= 255:
        green_is = PI.get_PWM_dutycycle(GREEN_PINS[0])
        green_diff = green - green_is
        green_list = _spread(green_diff, steps)
    if 0 <= blue <= 255:
        blue_is = PI.get_PWM_dutycycle(BLUE_PINS[0])
        blue_diff = blue - blue_is
        blue_list = _spread(blue_diff, steps)
    for i in range(steps):
        if red_list[i] is not 0:
            red_is += red_list[i]
        if green_list[i] is not 0:
            green_is += green_list[i]
        if blue_list[i] is not 0:
            blue_is += blue_list[i]
        _set_pins(red_is, green_is, blue_is)


@subscribe_to("system.onstart")
def start_func(key, data):
    """Test the 'onstart' event."""
    _set_pins(0, 0, 0)
    _crossfade(red=255, green=0, blue=0, speed=0.2)
    _crossfade(red=0, green=255, blue=0, speed=0.2)
    _crossfade(red=0, green=0, blue=255, speed=0.2)
    _crossfade(red=0, green=0, blue=0, speed=0.2)
    # _crossfade(255, 85, 17)
    return True


@subscribe_to("system.onexit")
def stop_func(key, data):
    """Test the 'onstart' event."""
    _crossfade(red=0, green=0, blue=0, speed=0.2)
    return True
