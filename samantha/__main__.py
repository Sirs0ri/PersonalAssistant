"""Samantha's main module. calling this via 'python samantha'
should start everything else"""
import logging
import logger

LOGGER = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.configure_logging()
    LOGGER.debug("-"*47)
    LOGGER.debug("Starting Samantha")
    LOGGER.debug("-"*47)
    LOGGER.info("I'm the main hanlder.")
    # TODO
    # load the context
    # Start the core
    # Initialize devices and services
    # Start updater as part of main
