"""Samantha's logging module.

- initializes a streamhandler, a TimedRotatingFileHandler and a custom
  AutoRemoteHandler with different formatters.
"""

###############################################################################
# pylint: disable=global-statement
#
# TODO: [ ] file_handler: if possible, rename logs to samantha.yyy-mm-dd.log
#           instead of samantha.log.yy-mm-dd at midnight
#           (-> 'time.strftime("%y-%m-%d")')
# TODO: [ ] upload/backup logfiles at midnight
#
###############################################################################


# standard library imports
import configparser
import logging
import logging.handlers
import os.path
import sys

# related third party imports
# import requests

# application specific imports
from . import handlers


__version__ = "1.6.0"


# Initialize the logger
LOGGER = logging.getLogger(__name__)

# Set constants
INITIALIZED = False

LOGGER.debug("I was imported.")


def _init(debug):
    """Configure Logging.

    Add a streamhandler, a TimedRotatingFileHandler and
    a custom AutoRemoteHandler. The latter one will be added only, if an API-
    Key is defined inside the file 'variables_private.ini'.
    """

    # STFU urllib3. For more info, see:
    # https://github.com/pypa/pip/issues/2681#issuecomment-92541888
    # requests.packages.urllib3.disable_warnings(
    #     requests.packages.urllib3.exceptions.SNIMissingWarning)
    # requests.packages.urllib3.disable_warnings(
    #     requests.packages.urllib3.exceptions.InsecurePlatformWarning)

    # Create the root-logger
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    logging._defaultFormatter = logging.Formatter(u"%(message)s")

    # Create the formatters. They'll be used throughout the application.
    # "hh:mm:ss,xxx LEVEL___ MODNAME_____ MESSAGE"
    nice_formatter = logging.Formatter(
        u"%(asctime)-8s,%(msecs)-3d %(levelname)-8s %(name)-12s\t%(message)s",
        "%X")
    # "yyyy-mm-dd hh:mm:ss,xxx LEVEL___ MODNAME_____ MESSAGE"
    full_formatter = logging.Formatter(
        u"%(asctime)-23s %(levelname)-8s %(name)-12s %(message)s")
    # "hh:mm:ss LEVEL MODNAME MESSAGE"
    practical_formatter = logging.Formatter(
        u"%(asctime)s %(levelname)s %(name)s %(message)s", "%X")

    # Create and add a handler to store the log in a textfile.
    # Level = DEBUG
    # Uses the full formatter (see above)
    # Switches to a new file each day at midnight

    # Get the path that leads to the logs-folder
    this_dir = os.path.split(__file__)[0]  # ..[1] would be the filename
    if this_dir is "":
        path = "../../data/logs"
    else:
        path = this_dir.replace("logger", "data/logs")

    if not os.path.exists(path):
        os.makedirs(path)
    file_handler = logging.handlers.TimedRotatingFileHandler(
        "{path}/samantha.log".format(path=path),
        when="midnight")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(full_formatter)
    root.addHandler(file_handler)

    # Create a handler that logs to the current commandline
    # Level = DEBUG
    # Uses the nice formatter (see above)
    # Displays the error levels nicely and colorful :3

    if "linux" in sys.platform:
        console_handler = handlers.ColorStreamHandler()
        if debug:
            console_handler.setLevel(logging.DEBUG)
        else:
            console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(nice_formatter)
        root.addHandler(console_handler)
        LOGGER.debug("Added the ColorStreamHandler.")
    else:
        console_handler2 = logging.StreamHandler()
        if debug:
            console_handler2.setLevel(logging.DEBUG)
        else:
            console_handler2.setLevel(logging.INFO)
        console_handler2.setFormatter(nice_formatter)
        root.addHandler(console_handler2)
        LOGGER.debug("Added the normal StreamHandler.")

    # Create and add a handler that sends errors to my phone via AutoRemote.
    # Level = WARN
    # Uses the practical formatter (see above)
    # Used to display warnings (or worse) on my phone as notification

    # If the variables_private.ini file doesn't exist, or doesn't contain the
    # key, the handler won't be added.
    config = configparser.ConfigParser()
    if (config.read("variables_private.ini")
            and config["autoremote"].get("api_key")):
        autoremote_handler = handlers.AutoRemoteHandler()
        # Set Handler to forward only important messages - WARN or higher
        autoremote_handler.setLevel(logging.ERROR)
        autoremote_handler.setFormatter(practical_formatter)
        root.addHandler(autoremote_handler)
    else:
        LOGGER.warn("The AutoRemote-Handler couldn't be started. Please make "
                    "sure the file 'variables_private.ini' exists inside the "
                    "/samantha folder and that it contains the AR-key in the "
                    "section [autoremote] as item 'api_key'.")

    LOGGER.info("All handlers were added successfully.")
    return True


def stop():
    """Stop the module."""
    global INITIALIZED

    LOGGER.info("Exiting...")
    # TODO stop logging.
    INITIALIZED = False
    LOGGER.info("Exited.")
    return True


def initialize(debug):
    """Initialize the module when not yet initialized."""
    global INITIALIZED
    if not INITIALIZED:
        INITIALIZED = _init(debug)
    else:
        LOGGER.info("Already initialized!")
