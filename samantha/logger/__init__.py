"""Samantha's logging module.

 - initializes a streamhandler, a TimedRotatingFileHandler and a custom
   AutoRemoteHandler with different formatters."""

###############################################################################
#
# TODO: [ ] _init()
# TODO: [ ]     create the logs-folder if it doesn't exist
# TODO: [ ] file_handler: if possible, rename logs to samantha.yyy-mm-dd.log
#           instead of samantha.log.yy-mm-dd at midnight
#           (-> 'time.strftime("%y-%m-%d")')
# TODO: [ ] upload/backup logfiles at midnight
# TODO: [ ] Set the ColorStreamHandler's level to INFO
#
###############################################################################


# standard library imports
import datetime
import logging
import logging.handlers
import os.path
import time

# related third party imports

# application specific imports
import handlers
from handlers import variables_private


__version__ = "1.5.4"


# Initialize the logger
LOGGER = logging.getLogger(__name__)

# Set constants
INITIALIZED = False

LOGGER.debug("I was imported.")


def _init(DEBUG):
    """Configure Logging. Add a streamhandler, a TimedRotatingFileHandler and
    a custom AutoRemoteHandler. The latter one will be added only, if an API-
    Key is defined inside the file 'variables_private.py'."""

    # Create the root-logger
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    # Create the formatters. They'll be used throughout the application.
    # "hh:mm:ss,xxx LEVEL___ MODNAME_____ MESSAGE"
    nice_formatter = logging.Formatter(
        "%(asctime)-8s,%(msecs)-3d %(levelname)-8s %(name)-12s\t%(message)s",
        "%X")
    # "yyyy-mm-dd hh:mm:ss,xxx LEVEL___ MODNAME_____ MESSAGE"
    full_formatter = logging.Formatter(
        "%(asctime)-23s %(levelname)-8s %(name)-12s %(message)s")
    # "hh:mm:ss LEVEL MODNAME MESSAGE"
    practical_formatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s", "%X")

    # Create and add a handler to store the log in a textfile.
    # Level = DEBUG
    # Uses the full formater (see above)
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

    # Create and add a handler that sends errors to my phone via AutoRemote.
    # Level = WARN
    # Uses the practical formater (see above)
    # Used to display warnings (or worse) on my phone as notification

    # If the variables_private.py file doesn't exist, or doesn't contain the
    # key, the handler won't be added.
    if variables_private and hasattr(variables_private, "ar_key"):
        autoremote_handler = handlers.AutoRemoteHandler()
        # Set Handler to forward only important messages - WARN or higher
        autoremote_handler.setLevel(logging.ERROR)
        autoremote_handler.setFormatter(practical_formatter)
        root.addHandler(autoremote_handler)
    else:
        LOGGER.warn("The AutoRemoteHandler couldn't be started. Please make "
                    "sure the file 'variables_private.py' exists inside the "
                    "/interface folder and that it contains the AR-key as a "
                    "variable called 'ar_key'.")

    # Create a handler that logs to the current commandline
    # Level = DEBUG
    # Uses the nice formater (see above)
    # Displays the error levels nicely and colorful :3

    console_handler = handlers.ColorStreamHandler()
    if DEBUG:
        console_handler.setLevel(logging.DEBUG)
    else:
        console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(nice_formatter)
    root.addHandler(console_handler)

    LOGGER.info("All handlers were added successfully.")
    return True


def stop():
    """Stops the module."""
    global INITIALIZED

    LOGGER.info("Exiting...")
    INITIALIZED = False
    LOGGER.info("Exited.")
    return True


def initialize(DEBUG):
    """Initialize the module when not yet initialized."""
    global INITIALIZED
    if not INITIALIZED:
        INITIALIZED = _init(DEBUG)
    else:
        LOGGER.info("Already initialized!")
