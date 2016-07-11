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


__version__ = "1.2.10"


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
        requests.post(url, payload, timeout=15)
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


@subscribe_to("media.twitch.*")
def notify_twitch(key, data):
    if "online" in key or "gamechange" in key:
        status = "online"
    else:
        status = "offline"
    message = \
        u"twitch=:={status}=:={c_name}=:={c_game}=:={c_status}=:={c_url}" \
        .format(status=status,
                c_name=data["channel"]["display_name"],
                c_game=data["channel"]["game"],
                c_status=data["channel"]["status"],
                c_url=data["channel"]["url"])
    files = [data["channel"]["logo"], data["channel"]["video_banner"]]
    return _send_ar_message(message, files)


@subscribe_to("time.time_of_day.*")
def notify_timeofday(key, data):
    """Notifiy the user about the sunset/rise for debugging purposes."""
    if ".day" in key:
        time_of_day = "day"
    elif ".night" in key:
        time_of_day = "night"
    else:
        time_of_day = "NaN"
    message = "logging=:=Samantha=:=It is now {}time.".format(time_of_day)
    return _send_ar_message(message)
