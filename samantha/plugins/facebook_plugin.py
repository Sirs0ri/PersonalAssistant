"""A plugin to test loading plugins. It doesn't do anything."""

###############################################################################
#
# TODO: [ ] Docs
#
###############################################################################


# standard library imports
import re
from HTMLParser import HTMLParser
import logging

# related third party imports
import requests

# application specific imports
from samantha.core import subscribe_to
from samantha.plugins.plugin import Plugin
from samantha.tools.eventbuilder import eEvent


def _init(curl):
    if curl is None:
        return None, None
    curl = curl.replace("curl ", "").replace(" --compressed", "")
    divider = curl[0]
    # this will be the type of quote around the items in the cURL command.
    # Should be ', but better safe than sound, right?
    curl = curl.replace(divider, "")  # remove all the quotes
    headers = curl.split(" -H ")
    url = headers.pop(0)
    header_dict = {}
    for h in headers:
        name, val = h.split(": ")
        header_dict[name] = val
    return url, header_dict

try:
    import samantha.variables_private as variables_private
    CURL = variables_private.fb_curl

except (ImportError, AttributeError):
    variables_private = None
    CURL = None


__version__ = "1.0.1"


# Initialize the logger
LOGGER = logging.getLogger(__name__)

PLUGIN = Plugin("Facebook", CURL is not None, LOGGER, __file__)

URL, HEADER_DICT = _init(CURL)

UNESCAPE = HTMLParser().unescape

CACHE = []


@subscribe_to("time.schedule.min")
def check_pokes(key, data):
    global CACHE

    cache = []
    new_count = 0
    req = requests.get(url=URL, headers=HEADER_DICT)
    text = req.text
    matches = re.findall(
        r'<article class="_55wr" id="poke_live_item_[\s\S]*?</article>',
        text)
    if matches:
        for match in matches:
            poke = {}

            m = re.search((r'<a href="/[\s\S]*?">'
                           r'(?P<name>[\s\S]*?)</a>'
                           r'(?P<text>[\s\S]*?)</div>'),
                          match)
            poke["text"] = m.group("name") + m.group("text")
            poke["name"] = m.group("name")
            m = re.search((r'<i class="img profpic"[\s\S]*?url\(&quot;'
                           r'(?P<imgurl>[\s\S]*?)&quot;\)'),
                          match)
            poke["imgurl"] = UNESCAPE(m.group("imgurl"))
            m = re.search((r'<a class="_56bz _54k8 _56bs _56bu" href="'
                           r'(?P<pokeurl>[\s\S]*?)"'),
                          match)
            poke["pokeurl"] = "https://m.facebook.com" + UNESCAPE(
                m.group("pokeurl"))

            if poke["name"] not in CACHE:
                LOGGER.warn(poke["text"])
                Event(sender_id=PLUGIN.name,
                      keyword="facebook.poked",
                      data=poke).trigger()
                new_count += 1
            else:
                LOGGER.warn("This poke by %s is an old one.", poke["name"])
            cache.append(poke["name"])
    else:
        LOGGER.warn("No new pokes!")

    CACHE = cache

    return "Found {} poke{}, {} of them new. ({})".format(
        len(CACHE),
        "s" if len(CACHE) is not 1 else "",
        new_count,
        CACHE)


@subscribe_to("facebook.poke")
def poke(key, data):
    if "pokeurl" not in data:
        result = "Error: The URL is missing from the data."
    elif "headers" not in data:
        result = "Error: The headers are missing from the data."
    elif "name" not in data:
        result = "Error: The poked person's name is missing from the data."
    else:
        req = requests.get(url=data["pokeurl"], headers=data["headers"])
        if req.status_code == 200:
            result = "{} poked successfully".format(data["name"])
        else:
            result = "Error: the Poke returned Code {}".format(req.status_code)
    return result
