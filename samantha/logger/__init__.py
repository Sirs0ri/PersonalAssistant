"""This file contains the function to initialize logging. It'll initialize the
different Handlers as necessary."""

import logging
import logging.handlers
import os.path
import time
import handlers
from handlers import variables_private

LOGGER = logging.getLogger(__name__)


def configure_logging():
    """Configure Logging. Add a streamhandler, a TimedRotatingFileHandler and
    a custom AutoRemoteHandler. The latter one will be added only, if an API-
    Key is defined inside the file 'variables_private.py'."""

    # create the logger
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    # create the formatters. They'll be used throughout the application.
    # hh:mm:ss LEVEL___ MODNAME_____ MESSAGE
    nice_formatter = logging.Formatter(
        "%(asctime)s %(levelname)-8s %(name)-12s %(message)s",
        time.strftime("%X"))
    # yyyy-mm-dd hh:mm:ss,xxx LEVEL___ MODNAME_____ MESSAGE
    full_formatter = logging.Formatter(
        "%(asctime)s %(levelname)-8s %(name)-12s %(message)s")
    # hh:mm:ss LEVEL MODNAME MESSAGE
    practical_formatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s",
        time.strftime("%X"))

    # create and add a handler to store the log in a textfile.
    this_dir = os.path.split(__file__)[0]  # ..[1] would be the filename
    file_handler = logging.handlers.TimedRotatingFileHandler(
        "{this_dir}\\samantha.log".format(this_dir=this_dir),
        when="midnight")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(full_formatter)
    root.addHandler(file_handler)

    # create and add a handler that sends errors to my phone via AutoRemote.
    # if the variables_private.py file doesn't exist, or doesn't contain the
    # key, the handler won't be added.
    if variables_private and hasattr(variables_private, "ar_key"):
        autoremote_handler = handlers.AutoRemoteHandler()
        # Set Handler to forward only important messages - WARN or higher
        autoremote_handler.setLevel(logging.WARN)
        autoremote_handler.setFormatter(practical_formatter)
        root.addHandler(autoremote_handler)
    else:
        root.warn("The AutoRemoteHandler couldn't be started. Please make "
                  "sure the file 'variables_private.py' exists inside the "
                  "/interface folder and that it contains the AR-key as a "
                  "variable called 'ar_key'")

    # create a handler that logs to the current commandline - not enabled now,
    # but it might be useful later for debugging.
    console_handler = handlers.ColorStreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(nice_formatter)
    root.addHandler(console_handler)
    LOGGER.info("All handlers were added successfully.")
