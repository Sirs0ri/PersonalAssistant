"""A plugin to test loading devices. It doesn't do anything."""

###############################################################################
#
# TODO: [ ] Add a receiver to intercept commands from the remote
#
###############################################################################


# standard library imports
import logging
import time

# related third party imports
try:
    import pigpio
except ImportError:
    pigpio = None

# application specific imports
from samantha.core import subscribe_to
from samantha.plugins.plugin import Plugin, Device


__version__ = "1.0.8"

# Initialize the logger
LOGGER = logging.getLogger(__name__)


class Transmitter(object):
    """
    A class to transmit the wireless codes sent by 433 MHz
    wireless fobs. This class is taken 1:1 from:
    """
    # TODO: ADDRESS!

    def __init__(self, pi, gpio, repeats=4, bits=24, gap=9000, t0=300, t1=900):
        """
        Instantiate with the Pi and the GPIO connected to the wireless
        transmitter.

        The number of repeats (default 6) and bits (default 24) may
        be set.

        The pre-/post-amble gap (default 9000 us), short pulse length
        (default 300 us), and long pulse length (default 900 us) may
        be set.
        """
        self.pi = pi
        self.gpio = gpio
        self.repeats = repeats
        self.bits = bits
        self.gap = gap
        self.t0 = t0
        self.t1 = t1

        self._make_waves()

        pi.set_mode(gpio, pigpio.OUTPUT)

    def _make_waves(self):
        """
        Generates the basic waveforms needed to transmit codes.
        """
        wf = []
        wf.append(pigpio.pulse(1 << self.gpio, 0, self.t0))
        wf.append(pigpio.pulse(0, 1 << self.gpio, self.gap))
        self.pi.wave_add_generic(wf)
        self._amble = self.pi.wave_create()

        wf = []
        wf.append(pigpio.pulse(1 << self.gpio, 0, self.t0))
        wf.append(pigpio.pulse(0, 1 << self.gpio, self.t1))
        self.pi.wave_add_generic(wf)
        self._wid0 = self.pi.wave_create()

        wf = []
        wf.append(pigpio.pulse(1 << self.gpio, 0, self.t1))
        wf.append(pigpio.pulse(0, 1 << self.gpio, self.t0))
        self.pi.wave_add_generic(wf)
        self._wid1 = self.pi.wave_create()

    def set_repeats(self, repeats):
        """
        Set the number of code repeats.
        """
        if 1 < repeats < 100:
            self.repeats = repeats

    def set_bits(self, bits):
        """
        Set the number of code bits.
        """
        if 5 < bits < 65:
            self.bits = bits

    def set_timings(self, gap, t0, t1):
        """
        Sets the code gap, short pulse, and long pulse length in us.
        """
        self.gap = gap
        self.t0 = t0
        self.t1 = t1

        self.pi.wave_delete(self._amble)
        self.pi.wave_delete(self._wid0)
        self.pi.wave_delete(self._wid1)

        self._make_waves()

    def send(self, code):
        """
        Transmits the code (using the current settings of repeats,
        bits, gap, short, and long pulse length).
        """
        chain = [self._amble, 255, 0]

        bit = (1 << (self.bits - 1))
        for i in range(self.bits):
            if code & bit:
                chain += [self._wid1]
            else:
                chain += [self._wid0]
            bit = bit >> 1

        chain += [self._amble, 255, 1, self.repeats, 0]

        self.pi.wave_chain(chain)

        while self.pi.wave_tx_busy():
            time.sleep(0.1)

    def cancel(self):
        """
        Cancels the wireless code transmitter.
        """
        self.pi.wave_delete(self._amble)
        self.pi.wave_delete(self._wid0)
        self.pi.wave_delete(self._wid1)


if pigpio:
    PI = pigpio.pi("192.168.178.56")
else:
    PI = None
    LOGGER.error(
        "Could not import pigpio. Please follow the instructions on %s to "
        "install it manually.",
        "https://github.com/joan2937/pigpio/blob/master/README#L103")

if PI is not None and PI.connected:
    TRANSMITTER_PIN = 17
    TRANSMITTER = Transmitter(PI, gpio=TRANSMITTER_PIN)
    active = True
else:
    TRANSMITTER_PIN = None
    TRANSMITTER = None
    active = False
    LOGGER.error("Could not connect to the RasPi at 192.168.178.56.")

PLUGIN = Plugin("433", active, LOGGER, __file__)
READING_LAMP = Device("Readinglamp", active, LOGGER, __file__,
                      ["light", "433"])
AMBIENT_LAMP = Device("Ambientlamp", active, LOGGER, __file__,
                      ["light", "433"])
BED_LAMP = Device("Bedlamp", active, LOGGER, __file__,
                      ["light", "433"])


@READING_LAMP.turn_on
def rl_turn_on(key, data):
    """Turn on the Reading-Lamp."""
    TRANSMITTER.send(1361)
    return "Reading Lamp turned on."


@subscribe_to(["system.onexit", "time.time_of_day.day"])
@READING_LAMP.turn_off
def rl_turn_off(key, data):
    """Turn off the Reading-Lamp."""
    TRANSMITTER.send(1364)
    return "Reading Lamp turned off."


@BED_LAMP.turn_on
def bl_turn_on(key, data):
    """Turn on the Bed-Lamp."""
    TRANSMITTER.send(4433)
    return "Bed Lamp turned on."


@subscribe_to(["system.onexit", "time.time_of_day.day"])
@BED_LAMP.turn_off
def bl_turn_off(key, data):
    """Turn off the Bed-Lamp."""
    TRANSMITTER.send(4436)
    return "Bed Lamp turned off."


@AMBIENT_LAMP.turn_on
def al_turn_on(key, data):
    """Turn on the Ambient-Lamp."""
    TRANSMITTER.send(5201)
    return "Ambient Lamp turned on."


@subscribe_to(["system.onexit", "time.time_of_day.day"])
@AMBIENT_LAMP.turn_off
def al_turn_off(key, data):
    """Turn off the Ambient-Lamp."""
    TRANSMITTER.send(5204)
    return "Ambient Lamp turned off."

# @subscribe_to("system.onstart")
# def start_func(key, data):
#     """Start the receiver."""
#     LOGGER.debug("I'm now doing something productive!")
#     return True
#
#
# @subscribe_to("system.onexit")
# def stop_func(key, data):
#     """Stop the receiver."""
#     LOGGER.debug("I'm not doing anything productive anymore.")
#     return True
