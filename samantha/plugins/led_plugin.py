"""A plugin to control LEDs connected to another RasPi."""

###############################################################################
#
# TODO: [ ]
#
###############################################################################


# standard library imports
import logging
import math
import threading
import time

# related third party imports
try:
    import pigpio
except ImportError:
    pigpio = None

# application specific imports
from samantha.core import subscribe_to
from samantha.plugins.plugin import Device


__version__ = "1.3.12"


# Initialize the logger
LOGGER = logging.getLogger(__name__)

NEW_COMMAND = threading.Event()
IDLE = threading.Event()
IDLE.set()

if pigpio:
    PI = pigpio.pi("192.168.178.56")
else:
    PI = None
    LOGGER.error(
        "Could not import pigpio. Please follow the instructions on %s to "
        "install it manually.",
        "https://github.com/joan2937/pigpio/blob/master/README#L103")

if PI is not None and PI.connected:
    RED_PINS = [12, 25]
    GREEN_PINS = [20, 23]
    BLUE_PINS = [21, 18]
else:
    RED_PINS = []
    GREEN_PINS = []
    BLUE_PINS = []
    LOGGER.error("Could not connect to the RasPi at 192.168.178.56.")

# PLUGIN = Device("LED", False, LOGGER, __file__, "light")
PLUGIN = Device("LED", PI.connected, LOGGER, __file__, "light")

BRIGHTNESS = 0.0
R_COLOR = 0.0
G_COLOR = 0.0
B_COLOR = 0.0


def _sleep(duration):
    """Sleep if the currently executed command is the newest one."""
    if not NEW_COMMAND.is_set():
        time.sleep(duration)


# def dec2hex(dc):
#     """Return the hex representation of the given number as string.
#
#     The dec-value can be an int, a float or a string representing a number.
#     It'll be rounded if necessary.
#     """
#     return hex(int(round(float(dc))))[2:]
#
#
# def hex2dec(hx):
#     """Return the hex representation of the given number as string.
#
#     The dec-value can be an int, a float or a string representing a number.
#     It'll be rounded if necessary.
#     """
#     return int(hx, 16)


def _stop_previous_command():
    """Stop the currently executed command.

    While some functions here "do their thing" and then are done, some may run
    in an endless loop (like the fade- or strobe-functions. This method makes
    sure that the currently executed command is stopped before another one is
    executed.
    """
    NEW_COMMAND.set()
    IDLE.wait()
    NEW_COMMAND.clear()
    IDLE.clear()


def _set_pins(red=-1, green=-1, blue=-1):
    global BRIGHTNESS, R_COLOR, G_COLOR, B_COLOR
    if 0 <= red <= 255 and not NEW_COMMAND.is_set():
        for pin in RED_PINS:
            PI.set_PWM_dutycycle(pin, red)
    if 0 <= green <= 255 and not NEW_COMMAND.is_set():
        for pin in GREEN_PINS:
            PI.set_PWM_dutycycle(pin, green)
    if 0 <= blue <= 255 and not NEW_COMMAND.is_set():
        for pin in BLUE_PINS:
            PI.set_PWM_dutycycle(pin, blue)
    red = red if 0 <= red <= 255 else R_COLOR
    green = green if 0 <= green <= 255 else G_COLOR
    blue = blue if 0 <= blue <= 255 else B_COLOR
    BRIGHTNESS = max(red, green, blue) / 255.0
    if BRIGHTNESS == 0:  # avoid a ZeroDivision error
        R_COLOR = 0
        G_COLOR = 0
        B_COLOR = 0
    else:
        R_COLOR = float(red) / BRIGHTNESS
        G_COLOR = float(green) / BRIGHTNESS
        B_COLOR = float(blue) / BRIGHTNESS
    # LOGGER.warn("R: %d, G: %d, B: %d, Brightness: %.2f",
    #             R_COLOR, G_COLOR, B_COLOR, BRIGHTNESS)


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
        """Linear function. linear(0) = 0, linear(length) = steps.
        |                   o
        |                 o  
        |              o     
        |            o       
        |         o          
        |       o            
        |    o               
        |  o                 
        +-------------------
        """
        return round(x*(steps/length))

    def squared(x):
        """Squared function. squared(0) = 0, squared(length) = steps.
        |                  o
        |                   
        |                o  
        |                   
        |             o     
        |           o       
        |        o          
        | o o  o            
        +-------------------
        """
        return round(x*x*(steps/(length*length)))

    def root(x):
        """Square root function. root(0) = 0, root(length) = steps.
        |                  o
        |             o     
        |        o          
        |      o            
        |   o               
        | o                 
        | o                 
        | o                 
        +-------------------
        """
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


def _crossfade(red=-1, green=-1, blue=-1, speed=1.0,
               brightness=1.0, interpolator=None):
    """Fade from the current color to another one."""
    if not NEW_COMMAND.is_set():
        if speed > 0:
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
            i = 0
            if not (red_is == red and blue_is == blue and green_is == green):
                # don't crossfade if none of the colors would change
                while i < steps and not NEW_COMMAND.is_set():
                    if red_list[i] is not 0:
                        red_is += red_list[i]
                    if green_list[i] is not 0:
                        green_is += green_list[i]
                    if blue_list[i] is not 0:
                        blue_is += blue_list[i]
                    _set_pins(red_is, green_is, blue_is)
                    i += 1
        else:
            r = red if 0 <= red <= 255 else \
                PI.get_PWM_dutycycle(RED_PINS[0])
            g = green if 0 <= green <= 255 else \
                PI.get_PWM_dutycycle(GREEN_PINS[0])
            b = blue if 0 <= blue <= 255 else \
                PI.get_PWM_dutycycle(BLUE_PINS[0])
            _set_pins(red=r, green=g, blue=b)


def _set_brightness(brightness):
    """Set the LEDs to a given brightness."""
    if not NEW_COMMAND.is_set():
        brightness = (0.0 if brightness <= 0 else
                      1.0 if brightness >= 1 else
                      brightness)
        LOGGER.debug("Setting the LEDs to %.2f%% brightness.", brightness*100)
        r = int(R_COLOR * brightness)
        g = int(G_COLOR * brightness)
        b = int(B_COLOR * brightness)
        _crossfade(red=r, green=g, blue=b, speed=0.2)


@subscribe_to("set.led.brightness")
def set_brightness(key, data):
    """Set the LEDs to a given brightness.

    The new value has to be in data["brightness"]. It can be any representation
    of a number, since it'll be cast to a float anyways.
    """
    if "brightness" in data:
        _stop_previous_command()
        _set_brightness(float(data["brightness"]))
        IDLE.set()
        return "Set the LEDs to {0:.2f}% brightness.".format(BRIGHTNESS*100)


@subscribe_to("system.onstart")
def start_func(key, data):
    """Test the LEDs during the 'onstart' event."""
    _stop_previous_command()
    _crossfade(red=0, green=0, blue=0, speed=0.0)
    _crossfade(red=255, green=0, blue=0, speed=0.2)
    _crossfade(red=0, green=255, blue=0, speed=0.2)
    _crossfade(red=0, green=0, blue=255, speed=0.2)
    _crossfade(red=0, green=0, blue=0, speed=0.2)
    IDLE.set()
    # _crossfade(255, 85, 17)
    return "Tested the LEDs."


@subscribe_to("led.fade")
def fade_func(key, data):
    """Test the LEDs during the 'onstart' event."""
    _stop_previous_command()

    while not NEW_COMMAND.is_set():
        _crossfade(red=255, green=0, blue=0)
        _crossfade(red=0, green=255, blue=0)
        _crossfade(red=0, green=0, blue=255)
    IDLE.set()
    return "The LEDs are now fading."


@subscribe_to("led.strobe")
def strobe_func(key, data):
    """Test the LEDs during the 'onstart' event."""
    _stop_previous_command()

    while not NEW_COMMAND.is_set():
        _crossfade(red=255, green=0, blue=0, speed=0.0)
        _sleep(0.1)
        _crossfade(red=0, green=255, blue=0, speed=0.0)
        _sleep(0.1)
        _crossfade(red=0, green=0, blue=255, speed=0.0)
        _sleep(0.1)
    IDLE.set()
    return "The LEDs are now strobing."


@subscribe_to("led.test")
def test_interpolators(key, data):
    """Test the different interpolators."""
    _stop_previous_command()
    _crossfade(red=0, green=0, blue=0, speed=0.2)
    _crossfade(red=255, green=0, blue=0, interpolator="sqrt")
    _crossfade(red=0, green=0, blue=0, speed=0.0)
    _sleep(0.5)
    _crossfade(red=255, green=0, blue=0, speed=0.0)
    _crossfade(red=0, green=0, blue=0, interpolator="sqrt")
    _sleep(0.5)
    _crossfade(red=0, green=255, blue=0, interpolator="linear")
    _crossfade(red=0, green=0, blue=0, speed=0.0)
    _sleep(0.5)
    _crossfade(red=0, green=255, blue=0, speed=0.0)
    _crossfade(red=0, green=0, blue=0, interpolator="linear")
    _sleep(0.5)
    _crossfade(red=0, green=0, blue=255, interpolator="squared")
    _crossfade(red=0, green=0, blue=0, speed=0.0)
    _sleep(0.5)
    _crossfade(red=0, green=0, blue=255, speed=0.0)
    _crossfade(red=0, green=0, blue=0, interpolator="squared")
    IDLE.set()
    return "Tested the LEDs."


@PLUGIN.turn_on
def turn_on(key, data):
    """Turn on all lights."""
    _stop_previous_command()
    _crossfade(red=255, green=85, blue=17, speed=0.2)
    IDLE.set()
    return "LEDs turned on."


@subscribe_to("increase.led.brightness")
def increase_brightness(key, data):
    """Increase brightness by 10%."""
    _stop_previous_command()
    brightness = BRIGHTNESS + 0.2
    brightness = (0.0 if brightness <= 0 else
                  1.0 if brightness >= 1 else
                  brightness)
    _set_brightness(brightness)
    IDLE.set()
    return "Increased the LEDs to {0:.2f}% brightness.".format(BRIGHTNESS*100)


@subscribe_to("decrease.led.brightness")
def decrease_brightness(key, data):
    """Decrease brightness by 10%."""
    _stop_previous_command()
    brightness = BRIGHTNESS - 0.2
    brightness = (0.0 if brightness <= 0 else
                  1.0 if brightness >= 1 else
                  brightness)
    _set_brightness(brightness)
    IDLE.set()
    return "Decreased the LEDs to {0:.2f}% brightness.".format(BRIGHTNESS*100)


@subscribe_to(["turn.on.ambient.led", "turn.on.ambient.light"])
def ambient_on(key, data):
    """Turn on light at 20% brightness."""
    _stop_previous_command()
    _set_brightness(0.2)
    IDLE.set()
    return "Set the lights to 20% brightness."


@subscribe_to(["turn.off.ambient.led", "turn.off.ambient.light"])
def ambient_off(key, data):
    """Turn on light at 100% brightness."""
    _stop_previous_command()
    _set_brightness(1)
    IDLE.set()
    return "Set the lights to 100% brightness."


@subscribe_to("time.time_of_day.day")
@PLUGIN.turn_off
@subscribe_to("system.onexit")
def turn_off(key, data):
    """Turn off all lights and (if the system is exiting) release resources."""
    _stop_previous_command()
    _crossfade(red=0, green=0, blue=0, speed=0.2)
    IDLE.set()
    result = "LEDs turned off"
    if key == "system.onexit":
        PI.stop()
        result += " and resources released"
    return result + "."
