"""Samantha's server.udp module."""


# standard library imports
import logging

# related third party imports

# application specific imports


__version__ = "1.0.0a1"

LOGGER = logging.getLogger(__name__)

LOGGER.info("I'm imported (server.udp_tools)")

def discover_servers():
    LOGGER.info("I'm checking")