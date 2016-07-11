"""Contains a baseclass for plugins."""

###############################################################################
#
# TODO: [ ] default methods
#
###############################################################################


# standard library imports
import logging

# related third party imports

# application specific imports


__version__ = "1.3.0"


# Initialize the logger
LOGGER = logging.getLogger(__name__)


class BaseClass(object):
    """Baseclass, that holds the mandatory methods a plugin must support."""

    def __init__(self, name="Device", active=False,
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
        self.logger.info("Initialisation complete")

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
