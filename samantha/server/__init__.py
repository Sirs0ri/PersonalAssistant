"""Samantha's server module."""


# standard library imports
import logging

# related third party imports

# application specific imports
from . import tcp_tools, tcp_server, \
              udp_tools, udp_server, \
              web_tools, web_server


__version__ = "1.0.0a1"

LOGGER = logging.getLogger(__name__)

LOGGER.info("I'm imported (server)")


def initialize(mode):
    LOGGER.info("initializing as %s.", mode)
    if mode == "master":
        web_server.start()