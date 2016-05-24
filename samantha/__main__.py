"""Samantha's main module. calling this via 'python samantha'
should start everything else"""
import logging
import Queue

# TODO import only what's necessary
import context
import core
import devices
import logger
import services
import tools


# Initialize the logger
logger.initialize()
LOGGER = logging.getLogger(__name__)


if __name__ == "__main__":
    LOGGER.info("Initializing...")
    LOGGER.debug("-"*47)
    LOGGER.debug("Starting Samantha")
    LOGGER.debug("-"*47)
    LOGGER.info("I'm the main handler.")

    INPUT = Queue.PriorityQueue()
    OUTPUT = Queue.PriorityQueue()

    context.initialize(INPUT, OUTPUT)
    core.initialize(INPUT, OUTPUT)
    devices.initialize(INPUT, OUTPUT)
    services.initialize(INPUT, OUTPUT)
    tools.initialize(INPUT, OUTPUT)

    # TODO
    # load the context
    # Initialize devices and services
    # Start updater as part of tools

    LOGGER.info("Initialisation complete.")
    tools.eventbuilder.Event(sender_id="i_main",
                             keyword="onstart").trigger()
    tools.server.run()

    tools.eventbuilder.Event(sender_id="i_main",
                             keyword="onexit").trigger()

    LOGGER.info("Exiting...")
    core.stop()
    context.stop()
    devices.stop()
    services.stop()
    tools.stop()
