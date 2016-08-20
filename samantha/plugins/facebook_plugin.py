"""A plugin to react to new pokes from Facebook.

It hijacks an authentication-cookie which the user has to enter manually.
Nomnomnom, Cookies!
"""

###############################################################################
#
# TODO: [ ]
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


try:
    import samantha.variables_private as variables_private
    CURL = variables_private.fb_curl

except (ImportError, AttributeError):
    variables_private = None
    CURL = None


__version__ = "1.0.2"


# Initialize the logger
LOGGER = logging.getLogger(__name__)

PLUGIN = Plugin("Facebook", CURL is not None, LOGGER, __file__)


def _parse_curl(curl):
    """Parse a cURL command meant to be used in bash into URL and headers.

    This plugin requires cookie-jacking to access and parse an authenticated
    version of Facebook's "poke" page. Chrome allows to copy internal URL call
    the browser makes including necessary cookies as bash commands. This
    function allows the user to enter this command and have it parsed.
    """
    if curl is None:
        return None, None
    curl = curl.replace("curl ", "").replace(" --compressed", "")
    divider = curl[0]
    # This will be the type of quote around the items in the cURL command.
    # Should always be ', but better safe than sound, right?
    curl = curl.replace(divider, "")  # remove all the quotes
    # The command is in the format "URL -H header1 -H header2 ..."
    # Everything before the first appearance of -H is the URL, after each
    # appearance of -H follows a header.
    headers = curl.split(" -H ")
    url = headers.pop(0)
    header_dict = {}
    for h in headers:
        name, val = h.split(": ")
        header_dict[name] = val
    return url, header_dict


# Parse a command formatted for bash's cURL into URL and a dict of headers.
URL, HEADER_DICT = _parse_curl(CURL)

# Initialize the HTMLParser only once to be used later.
UNESCAPE = HTMLParser().unescape

CACHE = []


@subscribe_to("time.schedule.min")
def check_pokes(key, data):
    """Parse the website https://m.facebook.com/pokes/ to access new pokes.

    The result is compared to an existing cache of pokes to notify the user
    only about new ones.
    """
    global CACHE

    cache = []
    new_count = 0
    req = requests.get(url=URL, headers=HEADER_DICT)
    text = req.text
    matches = re.findall(
        r'<article class="_55wr" id="poke_live_item_[\s\S]*?</article>',
        text)
    if matches:
        # pokes were found on the parsed webpage.
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
                LOGGER.debug(poke["text"])
                eEvent(sender_id=PLUGIN.name,
                       keyword="facebook.poked",
                       data=poke).trigger()
                new_count += 1
            else:
                LOGGER.warn("This poke by %s is an old one.", poke["name"])
            cache.append(poke["name"])
    else:
        LOGGER.warn("No new pokes!")

    CACHE = cache

    return "Found {} poke{}, {} of them new. (Cache: {})".format(
        len(CACHE),
        "s" if len(CACHE) is not 1 else "",
        new_count,
        CACHE)


@subscribe_to("facebook.poke")
def poke(key, data):
    """Poke a person via a URL including Facebook's authentication cookie."""
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
