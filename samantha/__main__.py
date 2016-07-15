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
import plugins
import logger
import tools


__version__ = "1.4.11"


if "--debug" in sys.argv or "-D" in sys.argv:
    DEBUG = True
else:
    DEBUG = False


# Initialize the logger
logger.initialize(DEBUG)
LOGGER = logging.getLogger(__name__)

if __name__ == "__main__":
    LOGGER.debug("-"*47)
    LOGGER.info("Initializing...")
    LOGGER.debug("-"*47)

    INPUT = Queue.PriorityQueue()
    OUTPUT = Queue.PriorityQueue()

    context.initialize(INPUT, OUTPUT)
    core.initialize(INPUT, OUTPUT)
    plugins.initialize(INPUT, OUTPUT)
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
    # INPUT.join()
    # OUTPUT.join()
    tools.stop()
    core.stop()
    context.stop()
    plugins.stop()
    LOGGER.debug("-"*47)
    LOGGER.info("Shutdown complete.")
    LOGGER.debug("-"*47)
