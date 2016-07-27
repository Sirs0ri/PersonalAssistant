"""Samantha's core module. Handles the processing of incoming commands.

- Reads the global INPUT queue
- Parses the incoming messages
- Forwards them to plugins
- puts results back into the OUTPUT queue

- Reads the global OUTOUT queue
- Sends outgoing messages back the the clients
"""

###############################################################################
# pylint: disable=global-statement
#
#           worker()
# TODO: [ ] parse the message
# TODO: [ ] allow a hierarchy in commands,
#           Example: "media.twitch.online.channename" will trigger plugins that
#           subscribed to "media.*", "*.online.*", "media.twitch.online.*", etc
#
###############################################################################


# standard library imports
from collections import Iterable
import ConfigParser
import datetime
from functools import wraps
import json
import logging
import math
import os
import Queue
import threading
import time
import traceback

# related third party imports

# application specific imports
# pylint: disable=import-error
import plugins
import tools
# pylint: enable=import-error


__version__ = "1.4.4"

# Initialize the logger
LOGGER = logging.getLogger(__name__)

# Set constants
INITIALIZED = False

NUM_WORKER_THREADS = 1
NUM_SENDER_THREADS = 1

INPUT = None
OUTPUT = None
STATUS = Queue.PriorityQueue()

FUNC_KEYWORDS = {}

UIDS = {}

LOGGER.debug("I was imported.")


def get_uid(prefix):
    """Generate an incrementing UID for unknown plugins."""
    if prefix in UIDS:
        UIDS[prefix] += 1
    else:
        UIDS[prefix] = 0
    uid = "{}_{:04}".format(prefix, UIDS[prefix])
    return uid


def _index(keyword, func):
    """Add a function to the index."""
    if not isinstance(keyword, str) and isinstance(keyword, Iterable):
        for key in keyword:
            if key not in FUNC_KEYWORDS:
                FUNC_KEYWORDS[key] = []
            FUNC_KEYWORDS[key].append(func)
    else:
        if keyword not in FUNC_KEYWORDS:
            FUNC_KEYWORDS[keyword] = []
        FUNC_KEYWORDS[keyword].append(func)
    tools.eventbuilder.update_keywords(FUNC_KEYWORDS)


def subscribe_to(keyword):
    """Add a function to the keyword-index. To be used as a decorator."""
    # code in this function is executed at runtime

    def decorator(func):
        """Add the decorated function to the index."""
        # code in this function is also executed at runtime
        LOGGER.debug("Decorating '%s.%s'. Key(s): %s..",
                     func.__module__,
                     func.__name__,
                     keyword)

        # Initialize the module
        mod = __import__(func.__module__, {}, {}, ('*', ))
        if hasattr(mod, "PLUGIN"):
            if mod.PLUGIN.is_active:
                if mod.PLUGIN.uid == "NO_UID":
                    LOGGER.debug("This is a new plugin..")
                    uid = get_uid(mod.PLUGIN.plugin_type)
                    mod.PLUGIN.uid = uid
                else:
                    LOGGER.debug("This is an existing plugin.")
                _index(keyword, func)
                LOGGER.debug("'%s.%s' decorated successfully.",
                             func.__module__,
                             func.__name__)
            else:
                LOGGER.debug("This is an inactive plugin.")
        elif func.__module__ == subscribe_to.__module__:
            LOGGER.debug("This function is part of the core.")
            _index(keyword, func)
        else:
            LOGGER.debug("This is an invalid plugin.")

        @wraps(func)
        def executer(*args, **kwargs):
            """Execute the decorated function."""
            # code in this function is executed once
            # the decorated function is executed
            return func(*args, **kwargs)

        return executer
    return decorator


@subscribe_to("wait")
def wait(key, data):
    """Wait five seconds."""
    time.sleep(5)
    return True


@subscribe_to(["logger", "logging"])
def change_logger(key, data):
    """Toggle the level of logging's ConsoleHandler between DEBUG and INFO."""
    root = logging.getLogger()
    if root.handlers[2].level == 10:
        root.handlers[2].setLevel(logging.INFO)
        LOGGER.warn("Logging-Level set to INFO")
        return True
    else:
        root.handlers[2].setLevel(logging.DEBUG)
        LOGGER.warn("Logging-Level set to DEBUG")
        return True


def stats_worker():
    """Read and process statusupdates from the STATUS queue."""
    # Used instead of the global LOGGER on purpose inside this function.

    @subscribe_to("time.schedule.day")
    def dummy(key, data):
        """Make sure that 'time.schedule.day' is indexed."""
        return True

    name = __name__ + "." + threading.current_thread().name
    logger = logging.getLogger(name)
    boot_time = datetime.datetime.now()
    success_functions_total = 0.0
    success_commands_total = 0.0
    failed_functions_total = 0.0
    failed_commands_total = 0.0
    count_requests_total = 0.0
    count_triggers_total = 0.0
    success_functions = 0.0
    success_commands = 0.0
    failed_functions = 0.0
    failed_commands = 0.0
    count_requests = 0.0
    count_triggers = 0.0
    while True:
        logger.debug("Waiting for an item.")
        event = STATUS.get()
        if event.event_type == "request":
            count_requests += 1
        else:
            count_triggers += 1
        processed = False
        for result in event.result.values():
            if (result is None or
                (isinstance(result, bool) and result is False) or
                (not isinstance(result, bool) and "Error: " in result)):
                failed_functions += 1
            else:
                success_functions += 1
                processed = True
        if processed:
            success_commands += 1
        else:
            failed_commands += 1

        if event.keyword in ["time.schedule.day", "system.onexit"]:
            logger.debug("Generating the daily report.")
            success_functions_total += success_functions
            success_commands_total += success_commands
            failed_functions_total += failed_functions
            failed_commands_total += failed_commands
            count_requests_total += count_requests
            count_triggers_total += count_triggers
            uptime = str(datetime.datetime.now() - boot_time).split(".")[0]
            count_commands = success_commands + failed_commands
            success_rate_commands = success_commands / count_commands * 100.0
            count_functions = success_functions + failed_functions
            success_rate_functions = (
                success_functions / count_functions * 100.0)
            count_commands_total = (
                success_commands_total + failed_commands_total)
            success_rate_commands_total = (
                success_commands_total / count_commands_total * 100.0)
            count_functions_total = (
                success_functions_total + failed_functions_total)
            success_rate_functions_total = (
                success_functions_total / count_functions_total * 100.0)
            report = ("<b>Past 24h:</b><br>"
                      "{:.0f} Triggers, {:.0f} Requests<br>"
                      "Processed commands: {:.0f} ({:.2f}% success)<br>"
                      "Processed functions: {:.0f} ({:.2f}% success)<br><br>"
                      "<b>All Time (Uptime: {!s}):</b><br>"
                      "{:.0f} Triggers, {:.0f} Requests<br>"
                      "Processed commands: {:.0f} ({:.2f}% success)<br>"
                      "Processed functions: {:.0f} ({:.2f}% success)".format(
                          count_triggers, count_requests, count_commands,
                          success_rate_commands, count_functions,
                          success_rate_functions, uptime, count_triggers_total,
                          count_requests_total, count_commands_total,
                          success_rate_commands_total, count_functions_total,
                          success_rate_functions_total))
            tools.eventbuilder.Event(sender_id=name,
                                     keyword="notify.user",
                                     data={"title": "Daily report",
                                           "message": report}).trigger()
            success_functions = 0.0
            success_commands = 0.0
            failed_functions = 0.0
            failed_commands = 0.0
            count_requests = 0.0
            count_triggers = 0.0
        STATUS.task_done()


def worker():
    """Read and process commands from the INPUT queue.

    Puts results back into OUTPUT.
    """
    # Get a new logger for each thread.
    # Used instead of the global LOGGER on purpose inside this function.
    name = __name__ + "." + threading.current_thread().name
    logger = logging.getLogger(name)

    while True:
        # Wait until an item becomes available in INPUT
        logger.debug("Waiting for an item.")
        event = INPUT.get()

        logger.debug("[UID: %s] Now processing '%s' from %s",
                     event.uid,
                     event.keyword,
                     event.sender_id)

        if event.expired:
            logger.warn("[UID: %s] The event is expired and will be skipped.",
                        event.uid)
            event.result = {name: "Error: The event expired and was skipped."}
        else:

            if event.keyword == "onstart":
                logger.info("The index now has %d entries.",
                            len(FUNC_KEYWORDS))
                logger.debug("%s", FUNC_KEYWORDS.keys())

            results = {}
            for key_substring in event.parsed_kw_list:
                if key_substring in FUNC_KEYWORDS:
                    for func in FUNC_KEYWORDS[key_substring]:
                        try:
                            logger.debug("[UID: %s] Executing '%s.%s'.",
                                         event.uid,
                                         func.__module__,
                                         func.__name__)
                            res = func(key=event.keyword,
                                       data=event.data)
                            results["{}.{}".format(
                                func.__module__, func.__name__)] = res
                        except Exception as e:
                            logger.exception("Exception in user code:\n%s",
                                             traceback.format_exc())
                            res = "Error: " + str(e)
                            results["{}.{}".format(
                                func.__module__, func.__name__)] = res
            # results = [x for x in results if x]
            if not results:
                results[name] = "Error: No matching plugin found."

            event.result = results
            logger.info("[UID: %s] Processing of '%s' successful. "
                        "%d result%s: %s",
                        event.uid,
                        event.keyword,
                        len(results),
                        ("s" if len(results) > 1 else ""),
                        results)

        # Put the result back into the OUTPUT queue
        if event.event_type == "request":
            OUTPUT.put(event)

        # Put the processed event into STATUS to include it in the statistics
        STATUS.put(event)

        # Let the queue know that processing is complete
        INPUT.task_done()


def sender():
    """Read processed commands from OUTPUT queue; send them back to client."""
    # Get a new logger for each thread.
    # Used instead of the global LOGGER on purpose inside this function.
    logger = logging.getLogger(
        __name__ + "." + threading.current_thread().name)

    while True:
        # Wait until an item becomes available in OUTPUT
        logger.debug("Waiting for an item.")
        message = OUTPUT.get()

        logger.debug("[UID: %s] Got the Item '%s'",
                     message.uid,
                     message.keyword)

        # If the message was a request...
        if message.event_type == "request":
            # ...send it's result back to where it came from
            logger.debug("[UID: %s] Sending the result back",
                         message.uid)
            if message.sender_id[0] == "c":
                # Original message came from a client via the server
                logger.debug("Sending the result '%s' back to client %s",
                             message.result, message.sender_id)
                tools.server.send_message(message)
            elif message.sender_id[0] == "d":
                # Original message came from a device-plugin
                logger.debug("Sending results to devices isn't possible yet.")
            elif message.sender_id[0] == "s":
                # Original message came from a service-plugin
                logger.debug("Sending results to services isn't possible yet.")
            else:
                logger.warn("Invalid UID: %s", message.sender_id)
        else:
            logger.debug("[UID: %s] Not sending the result back since the "
                         "event was a trigger.", message.uid)

        logger.info("[UID: %s] Processing of '%s' completed.",
                    message.uid,
                    message.keyword)

        # Let the queue know that processing is complete
        OUTPUT.task_done()


def _init(queue_in, queue_out):
    """Initialize the module."""
    global INPUT, OUTPUT, NUM_WORKER_THREADS, NUM_SENDER_THREADS

    LOGGER.info("Initializing...")
    INPUT = queue_in
    OUTPUT = queue_out

    # Read the number of threads to start from Samantha's config file
    # (/samantha/data/samantha.cfg)
    LOGGER.debug("Reading the config file...")
    # get the config file's path in realtion to the path of this file
    this_dir = os.path.split(__file__)[0]  # ..[1] would be the filename
    if this_dir is "":
        path = "../../data"
    else:
        path = this_dir.replace("core", "data")

    config = ConfigParser.RawConfigParser()
    config.read("{path}/samantha.cfg".format(path=path))

    try:
        # This leads to approx. X worker, X/2 sender and X/4 stat-threads.
        NUM_WORKER_THREADS = config.getint(__name__, "NUM_WORKER_THREADS")
        NUM_SENDER_THREADS = int(math.ceil(1.0 * NUM_WORKER_THREADS / 2))
        NUM_STATISTICS_THREADS = int(math.ceil(1.0 * NUM_WORKER_THREADS / 4))
    except Exception:
        LOGGER.exception("Exception while reading the config:\n%s",
                         traceback.format_exc())

    # Start the worker threads to process commands
    LOGGER.debug("Starting Worker")
    for i in range(NUM_WORKER_THREADS):
        thread = threading.Thread(target=worker, name="worker%d" % i)
        thread.daemon = True
        thread.start()

    # Start the sender threads to process results
    LOGGER.debug("Starting Sender")
    for i in range(NUM_SENDER_THREADS):
        thread = threading.Thread(target=sender, name="sender%d" % i)
        thread.daemon = True
        thread.start()

    # Start the statistics thread to process results
    LOGGER.debug("Starting Statistics-Thread")
    for i in range(NUM_STATISTICS_THREADS):
        thread = threading.Thread(target=stats_worker, name="stats%d" % i)
        thread.daemon = True
        thread.start()

    LOGGER.info("Initialisation complete.")
    return True


def stop():
    """Stop the module."""
    global INITIALIZED

    LOGGER.info("Exiting...")
    LOGGER.warn("Waiting for INPUT to be emptied. It currently holds "
                "%d items.", INPUT.qsize())
    INPUT.join()
    LOGGER.warn("Waiting for OUTPUT to be emptied. It currently holds "
                "%d items.", OUTPUT.qsize())
    OUTPUT.join()
    LOGGER.warn("Waiting for STATUS to be emptied. It currently holds "
                "%d items.", STATUS.qsize())
    STATUS.join()

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
