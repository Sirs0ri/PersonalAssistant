"""Contains a baseclass for plugins."""

###############################################################################
#
# TODO: [ ] default methods
#
###############################################################################


# standard library imports
from collections import Iterable
from functools import wraps
import logging

# related third party imports

# application specific imports
# pylint: disable=import-error
from core import subscribe_to
# pylint: enable=import-error


__version__ = "1.4.5"


# Initialize the logger
LOGGER = logging.getLogger(__name__)


class Plugin(object):
    """Baseclass, that holds the mandatory methods a plugin must support."""

    def __init__(self, name="Plugin", active=False,
                 logger=None, file_path=None, plugin_type="s"):
        """Set the plugin's attributes, if they're not set already."""
        self.name = name
        self.uid = "NO_UID"
        self.is_active = active
        if logger:
            self.logger = logger
        else:
            self.logger = LOGGER
        if file_path:
            self.path = file_path
        else:
            self.path = __file__
        self.plugin_type = plugin_type
        plugin_type_long = "device" if self.plugin_type is "d" else "plugin"
        self.logger.info("Initialisation of the %s '%s' complete. "
                         "The %s is %sactive.",
                         plugin_type_long,
                         self.name,
                         plugin_type_long,
                         "" if self.is_active else "not ")

    def __str__(self):
        """Return a simple string representation of the plugin."""
        return "{} '{}', UID {}".format(
            ("Device" if self.plugin_type == "d" else "Plugin"),
            self.name,
            self.uid)

    def __repr__(self):
        """Return a verbose string representation of the plugin."""
        return "{type}\t{name:10}\tUID {uid}\tLoaded from {path}".format(
            type=("Device" if self.plugin_type == "d" else "Plugin"),
            name=self.name,
            uid=self.uid,
            path=self.path)


class Device(Plugin):
    """Baseclass, that holds the mandatory methods a device must support."""

    def __init__(self, name="Device", active=False,
                 logger=None, file_path=None, group=None):
        """Set the plugin's attributes, if they're not set already."""
        self.name = name
        self.is_available = None
        self.group = group
        self.power_on_keywords = ["turn.on." + self.name.lower()]
        self.power_off_keywords = ["turn.off." + self.name.lower()]
        if group:
            if not isinstance(group, str) and isinstance(group, Iterable):
                top_level = []
                sub_level = []
                words = []
                for key in group:
                    if key[-1] == ".":
                        sub_level.append(key)
                    else:
                        top_level.append(key)
                        words.append(key)
                for sub in sub_level:
                    for top in top_level:
                        words.append(sub + top)
                for word in words:
                    self.power_on_keywords.append("turn.on." + word.lower())
                    self.power_off_keywords.append("turn.off." + word.lower())
            else:
                self.power_on_keywords.append("turn.on." + group.lower())
                self.power_off_keywords.append("turn.off." + group.lower())
        # self.logger.info("Initialisation complete")
        super(Device, self).__init__(name, active, logger, file_path, "d")

    def turn_on(self, func):
        @subscribe_to(self.power_on_keywords)
        @wraps(func)
        def function(*args, **kwargs):
            return func(*args, **kwargs)

        return function

    def turn_off(self, func):
        @subscribe_to(self.power_off_keywords)
        @wraps(func)
        def function(*args, **kwargs):
            return func(*args, **kwargs)

        return function
