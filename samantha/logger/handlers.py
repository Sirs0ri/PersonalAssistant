"""This class contains custom Handlers for Logging.

It contains the ColorStream-Handler that color-codes the Loglevels for better
readability or an AutoRemote-Handler that sends log messages to my phone.
"""

###############################################################################
#
# TODO: [ ]
#
###############################################################################


# standard library imports
import logging
import logging.handlers
import traceback

# related third party imports
import requests

# application specific imports
# Try importing variables_private.py for the AutoRemoteHandler. If it fails,
# the handler will be ignored later.
try:
    import variables_private
except ImportError:
    variables_private = None
# The file variables_private.py is in my .gitignore - for good reasons.
# It includes private API-Keys that I don't want online. However, if you want
# to be able to send AutoRemote-Messages (see: http://joaoapps.com/autoremote/
# for certain log entries, create that file inside the '/samantha' folder and
# add an entry called 'ar_key' for your private AutoRemote key
# (eg. "ar_key = 'YOUR_KEY_HERE'").


__version__ = "1.2.5"


# Initialize the logger
LOGGER = logging.getLogger(__name__)


class AutoRemoteHandler(logging.Handler):
    """A Handler that sends logging messages to AutoRemote.

    AutoRemote is a service that was initially built as a plugin for the
    Android App Tasker (http://tasker.dinglisch.net) which allows simple
    communication between two phones. Sending messages works easily via
    HTTP Postrequests to AutoRemote's server at
    https://autoremotejoaomgcd.appspot.com/sendmessage (see below for more info
    on how the URL is built). The messages are then processed further on the
    phone, for example to be displayed in a notification, or on the user's
    homescreen.
    """

    def emit(self, record):
        """Send the message via a POST request to AutoRemote."""
        logging.getLogger("requests").setLevel(logging.WARNING)
        message = self.format(record)
        url = "https://autoremotejoaomgcd.appspot.com/sendmessage"
        payload = {'key': variables_private.ar_key,
                   'message': "logging=:=Samantha=:=" + message}
        try:
            if (not record.name == "logger.handlers" or
                (record.name == "pychromecast.socket_client" and
                 "Failed to connect, retrying in" in message)):
                # skip messages that were caused by this very function and by
                # pychromecast's socket_client that throws errors for
                # unimportant events
                LOGGER.debug("Sending '%s(...)' via AutoRemote",
                             message.split("\n")[0])
                requests.post(url, payload, timeout=15)
            else:
                LOGGER.warn("This error was either caused by this class or by "
                            "a short DC from the Chromecast, it won't be sent "
                            "via AutoRemote.")
        except Exception:
            LOGGER.exception("Exception while connecting to AutoRemote:\n%s",
                             traceback.format_exc())


class ColorStreamHandler(logging.StreamHandler):
    """A Handler that prints colored messages to the current console.

    The messages appear in various colors by using ANSI-escape-sequences.
    """

    def emit(self, record):
        """Log the current record.

        Here, it reads the part of the record containing the levelname (such as
        "DEBUG" or "ERROR") and adds ANSI-escape-codes around it to change the
        color. (see: http://ascii-table.com/ansi-escape-sequences.php)

        The String "DEBUG" will be replaced by "\033[96mDEBUG\033[0m" this way,
        in which "\033[" is the beginning, "m" the end of the escape sequence
        and 96 the actual Formatter, in this case the code for Cyan foreground
        text.

        If the levelname specified in the Formatter should have a specific
        length, this length is kept. If the levelname isn't part of the
        Formatter, nothing changes.

        After transforming the string inside the given record, the printing is
        handled via the original StreamHandler.
        """
        fmt = self.formatter._fmt
        # Check if the levelname is even part of the current Formatter
        # If not, none of the transformations are necessary
        if "levelname" in fmt:
            levelname = ""
            colors = {"DEBUG": "96",     # light cyan
                      "INFO": "97",      # white
                      "WARNING": "93",   # yellow
                      "ERROR": "91",     # red
                      "CRITICAL": "95"}  # magenta

            # Find the actual part of the Formatter that formats the levelname
            fmt_placeholders = fmt.split(" ")
            for placeholder in fmt_placeholders:
                if "levelname" in placeholder:
                    # Set a local variable to what the Formatter would have
                    # done. This is so that any changes to the string's length
                    # (e.g. exactly 8 with "%(levelname)-8s") are preserved.
                    levelname = placeholder % {"levelname": record.levelname}
            # Replace the record's levelname with the modified version.
            record.levelname = "\033[{attr}m{lvlname}\033[0m".format(
                attr=colors[record.levelname],
                lvlname=levelname)
        super(ColorStreamHandler, self).emit(record)
