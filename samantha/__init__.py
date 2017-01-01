"""Samantha's main module."""


# standard library imports
import logging

# related third party imports

# application specific imports
from . import logger
from . import server

__version__ = "1.0.0a2"

LOGGER = logging.getLogger(__name__)

def run(debug=False, force_master=False, **kwargs):
    logger.initialize(True)
    LOGGER.info("running")
    mode = ("master" if force_master or not server.udp_tools.discover_servers()
            else "slave")
    server.initialize(mode)