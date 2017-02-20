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
import webcolors

# application specific imports
from samantha.core import subscribe_to
from samantha.plugins.plugin import Device


__version__ = "1.4.4"


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
    """Sleep while the currently executed command is the newest one."""
    if duration >= 1:
        i = 0
        while i < duration and not NEW_COMMAND.is_set():
            time.sleep(1)
            i += 1
    else:
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


def _set_pins(red=-1, green=-1, blue=-1, keepglobals=False):
    """Set the LEDs to the values from the parameters.

    This function will automatically update the globally stored values for the
    colors (if not specified otherwise via keepglobals) and brightness.
    """
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
    BRIGHTNESS = float(max(red, green, blue))
    if not keepglobals:
        if BRIGHTNESS == 0:  # avoid a ZeroDivision error
            R_COLOR = 0
            G_COLOR = 0
            B_COLOR = 0
        else:
            R_COLOR = float(red * (255.0/BRIGHTNESS))
            G_COLOR = float(green * (255.0/BRIGHTNESS))
            B_COLOR = float(blue * (255.0/BRIGHTNESS))
    # LOGGER.warn("R: %.2f, G: %.2f, B: %.2f, Brightness: %.2f",
    #             R_COLOR, G_COLOR, B_COLOR, BRIGHTNESS)
    # LOGGER.info("R: %.2f, G: %.2f, B: %.2f, Brightness: %.2f",
    #             red, green, blue, max(red, green, blue))


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
    else:
        if steps > 0:
            func = squared
        elif steps < 0:
            func = root
        else:
            func = linear

    # Create a 'length' long list with evenly distributed items [0 ... 'steps']
    result = [func(x) for x in range(1, int(length)+1)]
    # For each item, set the item to it's rounded difference to the item before
    val = 0.0
    for i, value in enumerate(result):
        result[i], val = int(value - val), value
    return result


def _crossfade(red=-1, green=-1, blue=-1, speed=1.0,
               brightnessonly=False, interpolator=None):
    """Fade from the current color to another one."""
    if not NEW_COMMAND.is_set():
        red_is = PI.get_PWM_dutycycle(RED_PINS[0])
        r_diff = 0 if red == -1 else red - red_is
        green_is = PI.get_PWM_dutycycle(GREEN_PINS[0])
        g_diff = 0 if green == -1 else green - green_is
        blue_is = PI.get_PWM_dutycycle(BLUE_PINS[0])
        b_diff = 0 if blue == -1 else blue - blue_is
        if speed > 0:
            steps = int(round(speed * max(
                (math.fabs(diff) for diff in (r_diff, g_diff, b_diff))
            )))
        else:
            steps = 1
        red_list = _spread(r_diff, steps, interpolator)
        green_list = _spread(g_diff, steps, interpolator)
        blue_list = _spread(b_diff, steps, interpolator)

        i = 0
        while i < steps and not NEW_COMMAND.is_set():
            # if red_list[i] is not 0:
            red_is += red_list[i]
            # if green_list[i] is not 0:
            green_is += green_list[i]
            # if blue_list[i] is not 0:
            blue_is += blue_list[i]
            _set_pins(red_is, green_is, blue_is, brightnessonly)
            i += 1


def _set_brightness(brightness, speed=0.2):
    """Set the LEDs to a given brightness between 0 and 255."""
    if not NEW_COMMAND.is_set():
        LOGGER.debug("Current vals:\t%f,\t%f,\t%f,\t%f",
                     R_COLOR, G_COLOR, B_COLOR, BRIGHTNESS)
        brightness = (0 if brightness < 0 else
                      255 if brightness > 255 else
                      brightness)
        LOGGER.debug("Setting the LEDs to %.2f%% brightness.",
                     (brightness/255) * 100)
        r = int(round(R_COLOR * brightness/255.0))
        g = int(round(G_COLOR * brightness/255.0))
        b = int(round(B_COLOR * brightness/255.0))
        _crossfade(red=r, green=g, blue=b, speed=speed, brightnessonly=True)
        LOGGER.debug("The new vals:\t%f,\t%f,\t%f,\t%f",
                     R_COLOR, G_COLOR, B_COLOR, BRIGHTNESS)


###############################################################################
#
# Registered functions
#
#   start_func
#   turn_on
#   turn_off
#
#   set_brightness
#   increase_brightness
#   decrease_brightness
#   ambient_on (set brightness to 20%)
#   ambient_off (set brightness to 100%)
#
#   fade_func
#   strobe_func
#   breathe_func
#
#   test_interpolators
#
###############################################################################


@subscribe_to("system.onstart")
def start_func(key, data):
    """Test the LEDs during the 'onstart' event.

    This function will transition from off to red to green to yellow to off.
    """
    _stop_previous_command()
    _crossfade(red=0, green=0, blue=0, speed=0.0)
    _crossfade(red=255, green=0, blue=0, speed=0.2)
    _crossfade(red=0, green=255, blue=0, speed=0.2)
    _crossfade(red=0, green=0, blue=255, speed=0.2)
    _crossfade(red=0, green=0, blue=0, speed=0.2)
    IDLE.set()
    # _crossfade(255, 85, 17)
    return "Tested the LEDs."


@PLUGIN.turn_on
def turn_on(key, data):
    """Turn on all lights."""
    _stop_previous_command()
    _crossfade(red=255, green=85, blue=17, speed=0.2)
    IDLE.set()
    return "LEDs turned on."


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


@subscribe_to("set.led.brightness")
def set_brightness(key, data):
    """Set the LEDs to a given brightness.

    The new value has to be in data["brightness"]. It can be any representation
    of a number, since it'll be cast to a float anyways. Additionally, a speed-
    parameter can be specified. It can be a value between 0 and 1, the default
    is 0.2 (since that results in a nice quick, yet smooth transition).
    """
    if "brightness" in data:
        _stop_previous_command()
        if "speed" in data and 0 <= float(data["speed"]) <= 1:
            speed = float(data["speed"])
        else:
            speed = 0.2
        _set_brightness(float(data["brightness"]), speed)
        IDLE.set()
        return "Set the LEDs to {0:.2f}% brightness.".format(
            (BRIGHTNESS/255) * 100)


@subscribe_to("set.led.color")
def set_brightness(key, data):
    """Set the LEDs to a given color.

    The new value has to be in data["color"]. It can be a hex-code (#RRGGBB or
    #RGB) or the name of the color following CSS3 standards (
    https://developer.mozilla.org/en-US/docs/Web/CSS/color_value).
    Additionally, a speed-parameter can be specified. It can be a value between
    0 and 1, the default is 0.2 (since that results in a nice quick, yet smooth
    transition).
    """
    if "color" in data:
        color = data["color"]
        LOGGER.warning("Setting color to %s", color)
        # if not isinstance(color, (str, unicode)):  # Python2
        # Python3 doesn't distinguish between normal and unicode strings anymore
        if not isinstance(color, str):
            return "Error: The specified color is not a string: {}"\
                .format(color)
        else:
            try:
                if "#" in color:
                    red, green, blue = webcolors.hex_to_rgb(color)
                else:
                    red, green, blue = webcolors.name_to_rgb(color)
            except ValueError:
                return "Error: The specified color '{}' has an illegal format"\
                    .format(color)

            _stop_previous_command()
            if "speed" in data and 0 <= float(data["speed"]) <= 1:
                speed = float(data["speed"])
            else:
                speed = 0.2

            _crossfade(red, green, blue, speed)
            IDLE.set()
            return "Set the LEDs to {}/{}.".format(
                color, (red, green, blue))


@subscribe_to("increase.led.brightness")
def increase_brightness(key, data):
    """Increase brightness by 10%."""
    _stop_previous_command()
    brightness = BRIGHTNESS + 25
    brightness = (0 if brightness < 0 else
                  255 if brightness > 255 else
                  brightness)
    _set_brightness(brightness)
    IDLE.set()
    return "Increased the LEDs to {0:.2f}% brightness.".format(
            (BRIGHTNESS/255) * 100)


@subscribe_to("decrease.led.brightness")
def decrease_brightness(key, data):
    """Decrease brightness by 10%."""
    _stop_previous_command()
    brightness = BRIGHTNESS - 25
    brightness = (0 if brightness < 0 else
                  255 if brightness > 255 else
                  brightness)
    _set_brightness(brightness)
    IDLE.set()
    return "Decreased the LEDs to {0:.2f}% brightness.".format(
            (BRIGHTNESS/255) * 100)


@subscribe_to(["turn.on.ambient.led", "turn.on.ambient.light"])
def ambient_on(key, data):
    """Turn on light at 20% brightness."""
    _stop_previous_command()
    _set_brightness(50)
    IDLE.set()
    return "Set the lights to 20% brightness."


@subscribe_to(["turn.off.ambient.led", "turn.off.ambient.light"])
def ambient_off(key, data):
    """Turn on light at 100% brightness."""
    _stop_previous_command()
    _sleep(1)
    _set_brightness(255)
    IDLE.set()
    return "Set the lights to 100% brightness."


@subscribe_to("led.fade")
def fade_func(key, data):
    """Test the LEDs during the 'onstart' event.

    To create a barely noticeably transition, the speed is kept at 1 instead of
    the otherwise usual 0.2.
    """
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


@subscribe_to("led.breathe")
def breathe_func(key, data):
    """Test the LEDs during the 'onstart' event."""
    _stop_previous_command()

    while not NEW_COMMAND.is_set():
        _set_brightness(brightness=150, speed=1.0)
        _set_brightness(brightness=255, speed=1.0)
    IDLE.set()
    return "The LEDs are now breathing."


@subscribe_to("led.test.interpolators")
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
