"""Another test device to test loading devices."""

###############################################################################
#
# TODO: [ ]
#
###############################################################################


# standard library imports
from collections import Iterable
import logging
import traceback

# related third party imports
import requests

# application specific imports
# pylint: disable=import-error
from core import subscribe_to
from services.service import BaseClass
try:
    import variables_private
    KEY = variables_private.ar_key
except (ImportError, AttributeError):
    variables_private = None
    KEY = None
# pylint: enable=import-error


__version__ = "1.2.4"


# Initialize the logger
LOGGER = logging.getLogger(__name__)

SERVICE = BaseClass("Notification", KEY is not None, LOGGER, __file__)


def _send_ar_message(message=None, files=None):
    """Send a message via AutoRemote."""
    url = "https://autoremotejoaomgcd.appspot.com/sendmessage"
    payload = {'key': KEY}
    if message:
        payload["message"] = message
    if files:
        if not isinstance(files, str) and isinstance(files, Iterable):
            payload["files"] = ",".join(files)
        else:
            payload["files"] = files
    try:
        LOGGER.debug("Sending '%s(...)' via AutoRemote",
                     message.split("\n")[0])
        # skip messages that were caused by this very function.
        requests.post(url, payload, timeout=3)
        return True
    except Exception:
        LOGGER.exception("Exception while connecting to AutoRemote:\n%s",
                         traceback.format_exc())
        return False


@subscribe_to("system.*")
def notify_system_event(key, data):
    """Notify the user about a system-wide event."""
    message = "logging=:=Samantha=:=New system-wide event: " + key
    return _send_ar_message(message)
