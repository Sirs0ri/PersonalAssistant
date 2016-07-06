"""Samantha's main module.

Calling this via 'python samantha' starts everything else."""


# standard library imports
import logging
import Queue
import sys

# related third party imports

# application specific imports
# TODO import only what's necessary
import context
import core
import devices
import logger
import services
import tools


__version__ = "1.4.8"


if "--debug" in sys.argv or "-D" in sys.argv:
    DEBUG = True
else:
    DEBUG = False


# Initialize the logger
logger.initialize(DEBUG)
LOGGER = logging.getLogger(__name__)

if __name__ == "__main__":
    LOGGER.info("Initializing...")
    LOGGER.debug("-"*47)
    LOGGER.fatal("Samantha started.")
    LOGGER.debug("-"*47)

    INPUT = Queue.PriorityQueue()
    OUTPUT = Queue.PriorityQueue()

    context.initialize(INPUT, OUTPUT)
    core.initialize(INPUT, OUTPUT)
    devices.initialize(INPUT, OUTPUT)
    services.initialize(INPUT, OUTPUT)
    tools.initialize(INPUT, OUTPUT)

    # TODO load the context
    # TODO Start updater as part of tools

    LOGGER.info("Initialisation complete.")
    tools.eventbuilder.Event(sender_id="i_main",
                             keyword="system.onstart").trigger()
    tools.server.run()

    tools.eventbuilder.Event(sender_id="i_main",
                             keyword="system.onexit").trigger()

    LOGGER.info("Exiting...")
    INPUT.join()
    OUTPUT.join()
    core.stop()
    context.stop()
    devices.stop()
    services.stop()
    tools.stop()
    LOGGER.debug("-"*47)
    LOGGER.fatal("Shutdown complete.")
    LOGGER.debug("-"*47)
