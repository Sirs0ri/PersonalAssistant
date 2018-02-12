"""Samantha's main module.

Calling this via 'python samantha' starts everything else."""


# standard library imports
import logging
import queue
import threading
# related third party imports

# application specific imports
# TODO import only what's necessary
from . import context
from . import core
from . import plugins
from . import logger
from . import tools


__version__ = "1.5.2"


def run(debug=True, plugin_filter=None):

    # Initialize the logger
    logger.initialize(debug)
    LOGGER = logging.getLogger(__name__)

    LOGGER.debug("-"*47)
    LOGGER.info("Initializing...")
    LOGGER.debug("-"*47)

    INPUT = queue.Queue()
    OUTPUT = queue.Queue()

    context.initialize(INPUT, OUTPUT)
    core.initialize(INPUT, OUTPUT)
    plugins.initialize(INPUT, OUTPUT, plugin_filter)
    tools.initialize(INPUT, OUTPUT)

    # TODO load the context
    # TODO Start updater as part of tools

    LOGGER.info("Initialisation complete.")
    tools.eventbuilder.eEvent(sender_id="i_main",
                              keyword="system.onstart").trigger()
    tools.server.run()

    tools.eventbuilder.eEvent(sender_id="i_main",
                              keyword="system.onexit").trigger()

    LOGGER.info("Exiting...")
    threads = threading._active
    msg = "Currently active threads:"
    for t in threads:
        msg += "\nName: {}, \tDaemon: {}, \talive:{}".format(
            threads[t].getName(),
            threads[t].daemon,
            threads[t].is_alive()
        )
    LOGGER.warning(msg)
    # INPUT.join()
    # OUTPUT.join()
    tools.stop()
    core.stop()
    context.stop()
    plugins.stop()
    LOGGER.debug("-"*47)
    LOGGER.info("Shutdown complete.")
    LOGGER.debug("-"*47)
