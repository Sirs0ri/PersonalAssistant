"""A plugin to control LEDs connected to another RasPi."""

###############################################################################
#
# TODO: [ ]
#
###############################################################################


# standard library imports
import logging
import math
import time

# related third party imports
try:
    import pigpio
except ImportError:
    pigpio = None

# application specific imports
# pylint: disable=import-error
from core import subscribe_to
from plugins.plugin import BaseClass
# pylint: enable=import-error


__version__ = "1.2.0"


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

PLUGIN = BaseClass("LED", PI.connected, LOGGER, __file__, plugin_type="d")


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


def _spread(steps, length=256, interpolator=None):
    """Spread an amount of 'steps' evenly in a list with 'length' items."""

    if length == 0:
        return []
    if steps == 0:
        return [0] * length

    # Convert the args to floats
    length = float(length)
    steps = float(steps)

    def linear(x):
        """Linear function. linear(0) = 0, linear(length) = steps."""
        return round(x*(steps/length))

    def squared(x):
        """Squared function. squared(0) = 0, squared(length) = steps."""
        return round(x*x*(steps/(length*length)))

    def root(x):
        """Square root function. root(0) = 0, root(length) = steps."""
        return round((steps*math.sqrt(length)*math.sqrt(x))/length)

    if interpolator == "linear" or (interpolator is None and steps == 0):
        func = linear
    elif interpolator == "squared" or (interpolator is None and steps > 0):
        func = squared
    elif interpolator == "sqrt" or (interpolator is None and steps < 0):
        func = root

    # Create a 'length' long list with evenly distributed items [0 ... 'steps']
    result = [func(x) for x in range(1, int(length)+1)]
    # For each item, set the item to it's rounded difference to the item before
    val = 0.0
    for i, value in enumerate(result):
        result[i], val = int(value - val), value
    return result


def _crossfade(red=-1, green=-1, blue=-1, speed=1.0, interpolator=None):
    """Fade from the current color to another one."""
    steps = int(256 * speed)
    if 0 <= red <= 255:
        red_is = PI.get_PWM_dutycycle(RED_PINS[0])
        red_list = _spread((red - red_is), steps, interpolator)
    if 0 <= green <= 255:
        green_is = PI.get_PWM_dutycycle(GREEN_PINS[0])
        green_list = _spread((green - green_is), steps, interpolator)
    if 0 <= blue <= 255:
        blue_is = PI.get_PWM_dutycycle(BLUE_PINS[0])
        blue_list = _spread((blue - blue_is), steps, interpolator)
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
    """Test the LEDs during the 'onstart' event."""
    _set_pins(0, 0, 0)
    _crossfade(red=255, green=0, blue=0, speed=0.2)
    _crossfade(red=0, green=255, blue=0, speed=0.2)
    _crossfade(red=0, green=0, blue=255, speed=0.2)
    _crossfade(red=0, green=0, blue=0, speed=0.2)
    # _crossfade(255, 85, 17)
    return True


@subscribe_to("test.led")
def test_interpolators(key, data):
    """Test the different interpolators."""
    _crossfade(0, 0, 0, 0.2)
    _crossfade(255, 0, 0, interpolator="sqrt")
    _set_pins(0, 0, 0)
    time.sleep(0.5)
    _set_pins(255, 0, 0)
    _crossfade(0, 0, 0, interpolator="sqrt")
    time.sleep(0.5)
    _crossfade(0, 255, 0, interpolator="linear")
    _set_pins(0, 0, 0)
    time.sleep(0.5)
    _set_pins(0, 255, 0)
    _crossfade(0, 0, 0, interpolator="linear")
    time.sleep(0.5)
    _crossfade(0, 0, 255, interpolator="squared")
    _set_pins(0, 0, 0)
    time.sleep(0.5)
    _set_pins(0, 0, 255)
    _crossfade(0, 0, 0, interpolator="squared")
    # _crossfade(255, 85, 17)
    return True


@subscribe_to("turn_on.led")
def turn_on(key, data):
    """Turn on all lights."""
    _crossfade(255, 85, 17, 0.2)
    return True


@subscribe_to(["system.onexit", "turn_off.led"])
def turn_off(key, data):
    """Turn off all lights."""
    _crossfade(0, 0, 0, 0.2)
    return True
