"""Samantha's plugins module.

- forwards commands to plugins (like set property COLOR of LED to GREEN)
- fires events into the INPUT queue when an plugin's status changes
  (e.g. if it becomes un-/available)
"""

###############################################################################
# pylint: disable=global-statement
#
# TODO: [ ] monitor status changes
#
###############################################################################


# standard library imports
import glob
import imp
import logging
import os.path

# related third party imports

# application specific imports
# pylint: disable=import-error
import core
# pylint: enable=import-error


__version__ = "1.2.1"


# Initialize the logger
LOGGER = logging.getLogger(__name__)

# Set constants
INITIALIZED = False

INPUT = None
OUTPUT = None

UID = 0

LOGGER.debug("I was imported.")


def get_uid():
    """Generate an incrementing UID for each plugin."""
    global UID
    uid = "d_{0:04d}".format(UID)
    UID += 1
    return uid


def _init(queue_in, queue_out):
    """Initialize the module."""
    global INPUT, OUTPUT

    LOGGER.info("Initializing...")
    INPUT = queue_in
    OUTPUT = queue_out

    # initialize all plugins
    LOGGER.debug("Searching for plugins...")
    this_dir = os.path.split(__file__)[0]  # ..[1] would be the filename
    files = glob.glob("{}/*_plugin.py".format(this_dir))
    LOGGER.debug("%d possible plugins found.", len(files))

    plugin_str = ""
    device_str = ""
    count = 0

    for plugin_file in files:
        LOGGER.debug("Trying to import %s...", plugin_file)

        try:
            name = plugin_file.replace("samantha/", "") \
                              .replace("/", ".") \
                              .replace("_plugin.py", "")
            plugin_source = imp.load_source(name, plugin_file)
            LOGGER.debug("Successfully imported %s", plugin_file)
            if hasattr(plugin_source, "PLUGIN"):
                if plugin_source.PLUGIN.is_active:
                    count += 1
                    if plugin_source.PLUGIN.plugin_type == "d":
                        device_str += "\n\t%r" % (plugin_source.PLUGIN)
                    else:
                        plugin_str += "\n\t%r" % (plugin_source.PLUGIN)
                    LOGGER.debug("%s is a valid plugin.", plugin_file)
                else:
                    LOGGER.debug("%s is marked as inactive.", plugin_file)
            else:
                LOGGER.warn("%s is missing the plugin-class!", plugin_file)
        except ImportError:
            LOGGER.warn("%s couldn't be imported successfully!", plugin_file)

    LOGGER.info("Initialisation complete.")

    LOGGER.debug("Imported %d plugins: %s%s", count, device_str, plugin_str)
    return True


def stop():
    """Stop the module and all associated plugins."""
    global INITIALIZED

    LOGGER.info("Exiting...")
    INITIALIZED = False

    LOGGER.info("Exited.")
    return True


def initialize(queue_in, queue_out):
    """Initialize the module when not yet initialized."""
    global INITIALIZED
    if not INITIALIZED:
        INITIALIZED = _init(queue_in, queue_out)
    else:
        LOGGER.info("Already initialized!")
