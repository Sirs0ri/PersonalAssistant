"""Samantha's main module. calling this via 'python samantha'
should start everything else"""
import logging

import logger

# TODO import only what's necessary
LOGGER = logging.getLogger(__name__)

if __name__ == "__main__":
    LOGGER.debug("-"*47)
    LOGGER.debug("Starting Samantha")
    LOGGER.debug("-"*47)
    LOGGER.info("I'm the main handler.")
    # TODO
    # load the context
    # Start the core
    # Initialize devices and services
    # Start updater as part of main
