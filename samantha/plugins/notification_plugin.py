"""A plugin to send notifications to the user."""

###############################################################################
#
# TODO: [ ]
#
###############################################################################


# standard library imports
from collections import Iterable
from datetime import datetime
import logging
import traceback

# related third party imports
import requests

# application specific imports
# pylint: disable=import-error
from core import subscribe_to
from plugins.plugin import Plugin
try:
    import variables_private
    KEY = variables_private.ar_key
except (ImportError, AttributeError):
    variables_private = None
    KEY = None
# pylint: enable=import-error


__version__ = "1.3.4"


# Initialize the logger
LOGGER = logging.getLogger(__name__)

PLUGIN = Plugin("Notification", KEY is not None, LOGGER, __file__)


def _send_ar_message(message=None, files=None):
    """Send a message via AutoRemote."""
    url = "https://autoremotejoaomgcd.appspot.com/sendmessage"
    payload = {'key': KEY}
    if message:
        payload["message"] = message
    if files:
        if not isinstance(files, str) and isinstance(files, Iterable):
            files = [str(x) for x in files]
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
    message = "logging=:=Samantha=:={} New system-wide event: {}".format(
        datetime.now().strftime("%H:%M"), key)
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


@subscribe_to("*.fritzbox.availability.*")
def notify_fritz_availability(key, data):
    if "online" in key:
        status = "online"
    else:
        status = "offline"
    message = u"logging=:=Network=:={} {} is now {}.".format(
        datetime.now().strftime("%H:%M"), data["name"], status)
    return _send_ar_message(message)


@subscribe_to("*.fritzbox.newdevice.*")
def notify_fritz_newdevice(key, data):
    """Notifiy the user about new devices in the network."""
    message = "logging=:=Samantha=:={} {} joined the network.".format(
        datetime.now().strftime("%H:%M"), data["name"])
    return _send_ar_message(message)


@subscribe_to("time.time_of_day.*")
def notify_timeofday(key, data):
    """Notifiy the user about the sunset/rise for debugging purposes."""
    if ".day" in key:
        time_of_day = "day"
    elif ".night" in key:
        time_of_day = "night"
    else:
        time_of_day = "NaN"
    message = "logging=:=Samantha=:={} It is now {}time.".format(
        datetime.now().strftime("%H:%M"), time_of_day)
    return _send_ar_message(message)
