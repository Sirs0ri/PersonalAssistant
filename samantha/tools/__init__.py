"""A collection of different tools Samantha might use.

 - Updater, to monitor it's sources on GitHub and automatically update to newer
   versions, if available and if a certain series of tests passes"""

###############################################################################
#
# TODO: [ ] Updater
# TODO: [ ]     Monitor Sources for the modules
# TODO: [ ]     Test new versions
# TODO: [ ]     replace them on-the-go if tests are passed
# TODO: [ ]     keep the old version as backup for a certain time (maybe check
#               every 24h and discard old versions 24h later if nothing's gone
#               wrong?)
#
###############################################################################


# standard library imports
import logging
import threading
import time

# related third party imports

# application specific imports
import eventbuilder
import server


__version__ = "1.3.2"


# Initialize the logger
LOGGER = logging.getLogger(__name__)

# Set constants
INITIALIZED = False

INPUT = None
OUTPUT = None

LOGGER.debug("I was imported.")


class Sleeper_Thread(threading.Thread):
    """Thread class with a stop() method. The thread sleeps for 'delay'
    seconds, then runs the target-function."""

    def __init__(self, *args, **kwargs):
        self.delay = kwargs.pop('delay', 0)
        super(Sleeper_Thread, self).__init__(*args, **kwargs)
        self.logger = logging.getLogger(self.name)
        self._stop = threading.Event()

    def run(self):
        self.logger.debug("Started the sleeper-thread.")
        i = 0
        while i < self.delay and not self.stopped():
            time.sleep(1)
            i += 1
        if self.stopped():
            self.logger.debug("Exited.")
        else:
            self.logger.debug("Running the delayed function.")
            super(Sleeper_Thread, self).run()

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()


def _init(InputQueue, OutputQueue):
    """Initializes the module."""
    global INPUT, OUTPUT

    LOGGER.info("Initializing...")
    INPUT = InputQueue
    OUTPUT = OutputQueue

    # initialize all tools
    eventbuilder.initialize(InputQueue, OutputQueue)
    server.initialize(InputQueue, OutputQueue)

    LOGGER.info("Initialisation complete.")
    return True


def stop():
    """Stops the module."""
    global INITIALIZED

    LOGGER.info("Exiting...")
    INITIALIZED = False

    # Stop all tools
    eventbuilder.stop()
    server.stop()

    LOGGER.info("Exited.")
    return True


def initialize(InputQueue, OutputQueue):
    """Initialize the module when not yet initialized."""
    global INITIALIZED
    if not INITIALIZED:
        INITIALIZED = _init(InputQueue, OutputQueue)
    else:
        LOGGER.info("Already initialized!")
