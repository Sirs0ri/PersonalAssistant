"""A service to test loading services. It doesn't do anything."""

###############################################################################
#
# TODO: [ ] Events when streams go offline
#
###############################################################################


# standard library imports
import json
import logging

# related third party imports
import requests

# application specific imports
# pylint: disable=import-error
from core import subscribe_to
from services.service import BaseClass
from tools import eventbuilder
try:
    import variables_private
    secrets = {
        "oauth_token": variables_private.twitch_oauth_token,
        "client_id": variables_private.twitch_client_id}
except (ImportError, AttributeError):
    variables_private = None
    secrets = None
# pylint: enable=import-error


__version__ = "1.2.1"

# Initialize the logger
LOGGER = logging.getLogger(__name__)

if variables_private is None:
    LOGGER.exception("Couldn't access the private variables.")
if secrets is None:
    LOGGER.exception("Couldn't access the API-Key and/or client-ID.")

service = BaseClass("Twitch", secrets is not None, LOGGER, __file__)

streamlist = []


@subscribe_to(["onstart", "schedule_min"])
def check_followed_streams(key, data):
    """Check for new online streams on twitch.tv."""
    global streamlist
    # Make the http-request
    url = "https://api.twitch.tv/kraken/streams/followed"
    req = requests.get(url, params=secrets)
    data = json.loads(req.text)
    new_streamlist = {}
    # parse the data
    if "streams" in data:
        # If so, streams are available
        data = data["streams"]
        for item in data:
            channelname = item["channel"]["name"]
            new_streamlist[channelname] = item
            if channelname not in streamlist:
                # That means the stream came online since the last check
                LOGGER.debug("'%s' is now online.", channelname)
                eventbuilder.Event(
                    sender_id=service.name,
                    keyword="media.twitch.online.{}".format(
                        item["channel"]["name"]),
                    data=item).trigger()
            else:
                LOGGER.debug("'%s' is still online.", channelname)
                # The stream is online and already was at the last check
                del streamlist[channelname]

    for channelname in streamlist:
        # self.streamlist now contains all those streams that were online
        # during the last check but have gone offline since.
        LOGGER.debug("'%s' is now offline.", channelname)
        eventbuilder.Event(
            sender_id=service.name,
            keyword="media.twitch.offline.{}".format(channelname),
            data=streamlist[channelname]).trigger()
    # update the existing streamlist with the new streams
    streamlist = new_streamlist
    return True


# class Service(BaseClass):
#     """Service that checks for online streams on twitch.tv."""
#
#     def __init__(self, uid):
#         """Initialize this device."""
#         LOGGER.info("Initializing...")
#         self.name = "Twitch"
#         self.uid = uid
#         self.keywords = ["onstart", "schedule_min"]
#         self.streamlist = []
#         try:
#             self.secrets = {
#                 "oauth_token": variables_private.twitch_oauth_token,
#                 "client_id": variables_private.twitch_client_id}
#             active = True
#         except AttributeError:
#             LOGGER.exception("Couldn't access the API-Key and/or client-ID.")
#             self.secrets = None
#             active = False
#         self.weather = None
#         super(Service, self).__init__(
#             logger=LOGGER, file_path=__file__, active=active)
#
#     def check_followed_streams(self):
#         """Check for new online streams on twitch.tv."""
#         # Make the http-request
#         url = "https://api.twitch.tv/kraken/streams/followed"
#         req = requests.get(url, params=self.secrets)
#         data = json.loads(req.text)
#         new_streamlist = {}
#         # parse the data
#         if "streams" in data:
#             # If so, streams are available
#             data = data["streams"]
#             for item in data:
#                 channelname = item["channel"]["name"]
#                 new_streamlist[channelname] = item
#                 if channelname not in self.streamlist:
#                     # That means the stream came online since the last check
#                     LOGGER.debug("'%s' is now online.", channelname)
#                     eventbuilder.Event(
#                         sender_id=self.name,
#                         keyword="media.twitch.online.{}".format(
#                             item["channel"]["name"]),
#                         data=item).trigger()
#                 else:
#                     LOGGER.debug("'%s' is still online.", channelname)
#                     # The stream is online and already was at the last check
#                     del self.streamlist[channelname]
#
#         for channelname in self.streamlist:
#             # self.streamlist now contains all those streams that were online
#             # during the last check but have gone offline since.
#             LOGGER.debug("'%s' is now offline.", channelname)
#             eventbuilder.Event(
#                 sender_id=self.name,
#                 keyword="media.twitch.offline.{}".format(channelname),
#                 data=self.streamlist[channelname]).trigger()
#         # update the existing streamlist with the new streams
#         self.streamlist = new_streamlist
#         return True
#
#     def stop(self):
#         """Exit this device."""
#         LOGGER.info("Exiting...")
#         return super(Service, self).stop()
#
#     def process(self, key, data=None):
#         """Process a command from the core."""
#         if key in ["onstart", "schedule_min"]:
#             return self.check_followed_streams()
#         else:
#             LOGGER.warn("Keyword not in use. (%s, %s)", key, data)
