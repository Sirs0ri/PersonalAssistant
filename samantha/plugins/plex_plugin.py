"""A plugin to interact with Plex Media Servers."""

###############################################################################
#
# Until version 1.0.0:
# TODO: [X] Discover Servers
# TODO: [ ] Access Libraries
# TODO: [ ]     - Notify about new shows/Movies
# TODO: [ ]     - Check for new episodes that aren't in the library yet
# TODO: [ ] Documentation
#
###############################################################################


# standard library imports
import configparser
import logging
import socket
import struct

# related third party imports
from plexapi.myplex import MyPlexAccount
from plexapi.exceptions import Unauthorized, BadRequest, NotFound
from plexapi.server import PlexServer

# application specific imports
from samantha.core import subscribe_to
from samantha.plugins.plugin import Plugin
# from samantha.tools import eventbuilder


__version__ = "1.0.0a5"

# Initialize the logger
LOGGER = logging.getLogger(__name__)
logging.getLogger("plexapi").setLevel(logging.WARN)
logging.getLogger("urllib3.connectionpool").setLevel(logging.WARN)

# TODO Wrap this in a function and make it callable via event
config = configparser.ConfigParser()
if config.read("variables_private.ini"):
    # this should be ['variables_private.ini'] if the config was found
    plex_config = config["plex"]
    SECRETS = (plex_config.get("username"),
               plex_config.get("password", raw=True))
else:
    LOGGER.warning("No config found! Are you sure the file %s exists?",
                   "samantha/variables_private.ini")
    SECRETS = None


def discover_local_servers():
    """Find Plex Media Servers on the local network.

    Heavily based on the function found at
    https://github.com/iBaa/PlexConnect/blob/master/PlexAPI.py
    """
    result = []

    # Find all Plex servers on the network via Plex' 'GDM' protocol
    gdm_ip = '239.0.0.250'
    gdm_port = 32414
    gdm_msg = 'M-SEARCH * HTTP/1.0'.encode("utf-8")
    gdm_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    gdm_socket.settimeout(1.0)
    ttl = struct.pack('b', 1)
    gdm_socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)
    try:
        LOGGER.debug("Checking for servers on the Network")
        gdm_socket.sendto(gdm_msg, (gdm_ip, gdm_port))
        while True:
            try:
                data, server = gdm_socket.recvfrom(1024)
                LOGGER.debug("Received data from %s:\n%s", server, data)
                result.append({'from': server, 'data': data})
            except socket.timeout:
                break
    finally:
        gdm_socket.close()

    # parse the responses received from the servers
    pms_list = {}
    if result:
        for response in result:
            update = {'ip': response.get('from')[0]}

            # Check if we had a positive HTTP response
            if "200 OK" in response.get('data').decode("utf-8"):
                for each in response.get('data').decode("utf-8").split('\n'):
                    # decode response data
                    update['discovery'] = "auto"

                    if "Content-Type:" in each:
                        update['content-type'] = each.split(':')[1].strip()
                    elif "Resource-Identifier:" in each:
                        update['uuid'] = each.split(':')[1].strip()
                    elif "Name:" in each:
                        update['serverName'] = each.split(':')[
                            1].strip()
                    elif "Port:" in each:
                        update['port'] = each.split(':')[1].strip()
                    elif "Updated-At:" in each:
                        update['updated'] = each.split(':')[1].strip()
                    elif "Version:" in each:
                        update['version'] = each.split(':')[1].strip()

            pms_list[update['uuid']] = update

    if pms_list == {}:
        LOGGER.debug("No servers discovered")
    else:
        s = "" if len(pms_list) == 1 else "s"
        LOGGER.debug("%d Server%s discovered:", len(pms_list), s)
        for uuid in pms_list:
            LOGGER.debug("%s at %s:%s",
                         pms_list[uuid]['serverName'],
                         pms_list[uuid]['ip'],
                         pms_list[uuid]['port'])
    return pms_list


def get_servers_from_account():
    if SECRETS is None:
        return {}
    try:
        account = MyPlexAccount(username=SECRETS[0], password=SECRETS[1])
        account_servers = {resource.clientIdentifier: resource
                           for resource in account.resources()
                           if "server" in resource.provides}
        return account_servers
    except Unauthorized:
        LOGGER.error("Could not authorize your account with the given "
                     "credentials.")
        return {}
    except BadRequest:
        LOGGER.error("Blabla")
        # TODO: retry
        return {}


def localize_remote_servers(local_servers, remote_servers):
    # Prepare one list for all locally available servers
    # and one for only remotely available servers
    locally_available_servers = []
    remotely_available_servers = []

    # Check for each remotely available if it happens to be in the same network
    for server_id in remote_servers:
        remote_server_resource = remote_servers[server_id]
        LOGGER.debug("Checking if server %s is available via the Internet.",
                     remote_server_resource.name)
        remote_server = None
        # local_server = None
        try:
            # Attempt connecting to the server
            remote_server = remote_server_resource.connect(ssl=True)
            LOGGER.debug("Success.")
        except NotFound:
            LOGGER.warning("The server %s isn't available via the Internet",
                           remote_server_resource.name)

        LOGGER.debug("Checking if server %s is available via LAN.",
                     remote_server_resource.name)
        if server_id in local_servers:
            # Server is on the same network
            local_server_data = local_servers[server_id]
            baseurl = "http://{}:{}".format(local_server_data["ip"],
                                            local_server_data["port"])
            try:
                LOGGER.debug("The server %s is available via LAN. Attempting "
                             "to replace remote version with local one...",
                             remote_server_resource.name)
                local_server = PlexServer(baseurl,
                                          remote_server_resource.accessToken)
                del(local_servers[server_id])
                locally_available_servers.append(local_server)
                LOGGER.debug("Connecting to %s via %s succeeded.",
                             remote_server_resource.name,
                             baseurl)
            except NotFound:
                LOGGER.warning("Couldn't connect to %s via %s.",
                               remote_server_resource.name,
                               baseurl)
                if remote_server is not None:
                    remotely_available_servers.append(remote_server)
                else:
                    LOGGER.debug("The server %s was skipped because it wasn't "
                                 "available in any way.",
                                 remote_server_resource.name)
        elif remote_server is not None:
            # Server wasn't found in the same Network
            LOGGER.debug("The server %s is not available locally. "
                         "Sam will be using the remote resource.",
                         remote_server_resource.name)
            remotely_available_servers.append(remote_server)
        else:
            LOGGER.debug("The server %s was skipped because it wasn't "
                         "available in any way.",
                         remote_server_resource.name)
    for server_id in local_servers:
        this_server = local_servers[server_id]
        LOGGER.warning("You don't seem to have access to the server %s "
                       "(ID: %s) at %s:%s via your account. Please check "
                       "your credentials.",
                       this_server["serverName"],
                       server_id,
                       this_server["ip"],
                       this_server["port"])

    return locally_available_servers, remotely_available_servers


local = discover_local_servers()
remote = get_servers_from_account()
LOCAL_SERVERS, REMOTE_SERVERS = localize_remote_servers(local, remote)
ALL_SERVERS = LOCAL_SERVERS + REMOTE_SERVERS
LOGGER.info("%d servers were found. %d of them are locally available, %d via "
            "the internet.",
            len(ALL_SERVERS),
            len(LOCAL_SERVERS),
            len(REMOTE_SERVERS))


PLUGIN = Plugin("Plex", bool(ALL_SERVERS), LOGGER, __file__)


@subscribe_to("system.onstart")
def start_func(key, data):
    """Test the 'onstart' event."""
    # TODO: Scan libraries & Update Context
    LOGGER.debug("I'm now doing something productive!")
    return "I'm now doing something productive!"


@subscribe_to("system.onexit")
def stop_func(key, data):
    """Test the 'onexit' event."""
    LOGGER.debug("I'm not doing anything productive anymore.")
    return "I'm not doing anything productive anymore."
