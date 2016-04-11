"""Samantha's main module. calling this via 'python samantha'
should start everything else"""
import logging
import log

LOGGER = logging.getLogger(__name__)

if __name__ == "__main__":
    log.configure_logging()
    LOGGER.debug("-"*47)
    LOGGER.debug("Starting Samantha")
    LOGGER.debug("-"*47)
    LOGGER.info("I'm the main.")
