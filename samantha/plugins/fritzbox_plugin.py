"""A plugin to test loading plugins. It doesn't do anything."""

###############################################################################
#
# TODO: [ ]
#
###############################################################################


# standard library imports
import logging

# related third party imports
try:
    from fritzconnection import FritzHosts
except ImportError:
    FritzHosts = None


# application specific imports
# pylint: disable=import-error
import context
from core import subscribe_to
from plugins.plugin import Device
from tools import eventbuilder
try:
    import variables_private
    PASSWORD = variables_private.fritzbox_password
except (ImportError, AttributeError):
    variables_private = None
    PASSWORD = None
# pylint: enable=import-error


__version__ = "1.0.4"


# Initialize the logger
LOGGER = logging.getLogger(__name__)


def _get_hosts_info():
    # Mute requests' logging < WARN while getting data from the FritzBox.
    # It would otherwise produce roughly 150 messages within a second or two.
    req_logger = logging.getLogger("requests.packages.urllib3.connectionpool")
    req_logger_originallevel = req_logger.level
    req_logger.setLevel(logging.WARN)

    # Update data from the FritzBox
    devices_list = FRITZBOX.get_hosts_info()

    # Reset requests' logging to its original level.
    req_logger.setLevel(req_logger_originallevel)
    return devices_list


authenticated = False

if variables_private is None:
    LOGGER.exception("Couldn't access the private variables.")
if PASSWORD is None:
    LOGGER.exception("Couldn't access the password.")

if FritzHosts:
    FRITZBOX = FritzHosts(address="192.168.178.1",
                          user="Samantha",
                          password=PASSWORD)
    try:
        _get_hosts_info()
        authenticated = True
    except KeyError:
        LOGGER.exception("The credentialy are invalid.")

PLUGIN = Device("FritzBox", authenticated, LOGGER, __file__)

DEVICES_DICT = context.get_children("network.devices", default={})
DEVICES_DICT_CACHE = context.get_children("network.devices", default={})


def _status_update(device):
    status = "online" if int(device["status"]) else "offline"
    eventbuilder.Event(
        sender_id=PLUGIN.name,
        keyword="network.fritzbox.availability.{}.{}".format(
            status, device["name"]),
        data=device).trigger()
    DEVICES_DICT[device["mac"]] = device
    context.set_property("network.devices.{}".format(device["mac"]), device)


@subscribe_to(["system.onstart", "time.schedule.10s"])
def update_devices(key, data):
    """Check for updated device-info."""
    ignored_macs = ["00:80:77:F2:71:23", None]
    # this list holds the mac-addresses of ignored devices. They won't be able
    # to trigger events such as coming on/offline or registering. The 1st
    # listed address is for example my printer which dis- and reconnects every
    # few minutes and only spams my logs.

    # Update data from the FritzBox
    devices_list = _get_hosts_info()

    devices_list = sorted(devices_list,
                          key=lambda item: item["name"].lower())
    for device in devices_list:
        if device["mac"] in ignored_macs:
            LOGGER.debug("Ignoring '%s' as requested from the user.",
                         device["name"])
        else:
            if device["mac"] not in DEVICES_DICT:
                eventbuilder.Event(
                    sender_id=PLUGIN.name,
                    keyword="network.fritzbox.newdevice.{}".format(
                        device["name"]),
                    data=device).trigger()
                _status_update(device)
            else:
                if (int(device["status"])
                        is int(DEVICES_DICT_CACHE[device["mac"]]["status"])
                        is not int(DEVICES_DICT[device["mac"]]["status"])):
                    _status_update(device)

            DEVICES_DICT_CACHE[device["mac"]] = device

    return True
