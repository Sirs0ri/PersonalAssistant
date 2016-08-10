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


__version__ = "1.0.11"


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
    try:
        FRITZBOX = FritzHosts(address="192.168.178.1",
                              user="Samantha",
                              password=PASSWORD)
        _get_hosts_info()
        authenticated = True
    except IOError:
        LOGGER.exception("Couldn't connect to a fritzbox at the default "
                         "address '192.168.178.1'!")
    except KeyError:
        LOGGER.exception("The credentials are invalid.")

PLUGIN = Device("FritzBox", authenticated, LOGGER, __file__)

DEVICES_DICT = context.get_children("network.devices", default={})


def _status_update(device):
    status = "online" if int(device["status"]) else "offline"
    LOGGER.debug("Updating device %s", device["mac"])
    eventbuilder.Event(
        sender_id=PLUGIN.name,
        keyword="network.fritzbox.availability.{}.{}".format(
            status, device["name"]),
        data=device).trigger()
    context.set_property("network.devices.{}".format(device["mac"]), device)


@subscribe_to(["system.onstart", "time.schedule.10s"])
def update_devices(key, data):
    """Check for updated device-info."""

    if key == "time.schedule.10s" and data[5] % 20 is not 0:
        return "Skipping this check since I'm only refreshing every 20 Sec."

    ignored_macs = ["00:80:77:F2:71:23", None]
    # this list holds the mac-addresses of ignored devices. They won't be able
    # to trigger events such as coming on/offline or registering. The 1st
    # listed address is for example my printer which dis- and reconnects every
    # few minutes and only spams my logs.

    # LOGGER.debug("The INDEX holds %d devices.", len(DEVICES_DICT))

    # Update data from the FritzBox
    devices_list = _get_hosts_info()

    devices_list = sorted(devices_list,
                          key=lambda item: item["name"].lower())

    count = 0
    ignored = 0
    new = 0
    updated = 0
    for device in devices_list:
        count += 1
        if device["mac"] in ignored_macs:
            ignored += 1
            LOGGER.debug("Ignoring '%s' as requested by the user.",
                         device["name"])
        else:
            c_device = context.get_value(
                "network.devices.{}".format(device["mac"]), None)
            if c_device is None:
                new += 1
                LOGGER.debug("%s is a new device.", device["mac"])
                eventbuilder.Event(
                    sender_id=PLUGIN.name,
                    keyword="network.fritzbox.newdevice.{}".format(
                        device["name"]),
                    data=device).trigger()
                _status_update(device)
            else:
                # LOGGER.debug("%s is a known device.", device["mac"])
                if (int(device["status"])
                        is int(DEVICES_DICT[device["mac"]]["status"])
                        is not int(c_device["status"])):
                    updated += 1
                    LOGGER.debug("Device: %d %s, Cache: %d %s, Context: %d %s",
                                 int(device["status"]), device["status"],
                                 int(DEVICES_DICT[device["mac"]]["status"]),
                                 DEVICES_DICT[device["mac"]]["status"],
                                 int(c_device["status"]), c_device["status"])
                    _status_update(device)
                # else:
                #     status = "online" if int(device["status"]) else "offline"
                #     LOGGER.debug("%s is still %s ('%s').",
                #                  device["mac"], status, device["status"])

            DEVICES_DICT[device["mac"]] = device

    return("Processed {} devices in total, {} of them new. Ignored {} and "
           "updated {}.".format(count, new, ignored, updated))
