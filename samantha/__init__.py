"""Samantha's main module."""


# standard library imports
import logging

# related third party imports

# application specific imports
from samantha import logger

__version__ = "1.0.0a1"

LOGGER = logging.getLogger(__name__)

def run(**kwargs):
    logger.initialize(True)
    LOGGER.info("running")