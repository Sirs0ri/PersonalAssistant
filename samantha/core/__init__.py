"""Samantha's core module. Handles the processing of incoming commands.

- Reads the global INPUT queue
- Parses the incoming messages
- Forwards them to plugins
- puts results back into the OUTPUT queue

- Reads the global OUTPUT queue
- Sends outgoing messages back the the clients
"""

###############################################################################
#
# TODO: [ ] clean up stats_worker
#           worker()
# TODO: [ ] parse the message
#
###############################################################################


# standard library imports
from collections import Iterable
from copy import copy
import configparser
import datetime
from functools import wraps
import json
import logging
import math
import os
import queue
import threading
import time

# related third party imports

# application specific imports
from samantha import tools


__version__ = "1.6.0a7"

# Initialize the logger
LOGGER = logging.getLogger(__name__)

# Set constants
INITIALIZED = False

INPUT = None
OUTPUT = None
STATUS = queue.Queue()

LOCK = threading.Lock()

FUNC_KEYWORDS = {}

UIDS = {}

LOGGER.debug("I was imported.")


def get_index():
    return copy(FUNC_KEYWORDS)


def set_index(index):
    global FUNC_KEYWORDS
    FUNC_KEYWORDS = index
    LOGGER.info("The index now has %d entries.",
                len(FUNC_KEYWORDS))
    LOGGER.debug("%s", FUNC_KEYWORDS.keys())


def clear_index():
    global FUNC_KEYWORDS
    FUNC_KEYWORDS = {}


def _get_uid(prefix):
    """Generate an incrementing UID for unknown plugins."""
    if prefix in UIDS:
        UIDS[prefix] += 1
    else:
        UIDS[prefix] = 0
    uid = "{}_{:04}".format(prefix, UIDS[prefix])
    return uid


def _index(keyword, func, version):
    """Add a function to the index."""
    if not isinstance(keyword, str) and isinstance(keyword, Iterable):
        for key in keyword:
            if key not in FUNC_KEYWORDS:
                FUNC_KEYWORDS[key] = []
            entry = {"name": ".".join([func.__module__, func.__name__]),
                     "version": version,
                     "func": func}
            FUNC_KEYWORDS[key].append(entry)
    else:
        if keyword not in FUNC_KEYWORDS:
            FUNC_KEYWORDS[keyword] = []
        entry = {"name": ".".join([func.__module__, func.__name__]),
                 "version": version,
                 "func": func}
        FUNC_KEYWORDS[keyword].append(entry)
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
                    uid = _get_uid(mod.PLUGIN.plugin_type)
                    mod.PLUGIN.uid = uid
                else:
                    LOGGER.debug("This is a known plugin.")
                _index(keyword, func, mod.__version__)
                LOGGER.debug("'%s.%s' decorated successfully.",
                             func.__module__,
                             func.__name__)
            else:
                LOGGER.debug("This is an inactive plugin.")
        elif func.__module__ == subscribe_to.__module__:
            LOGGER.debug("This function is part of the core.")
            _index(keyword, func, __version__)
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
    return "Waited for 5 seconds."


@subscribe_to(["logger", "logging"])
def change_logger(key, data):
    """Toggle the level of logging's ConsoleHandler between DEBUG and INFO."""
    root = logging.getLogger()
    if root.handlers[2].level == 10:
        root.handlers[2].setLevel(logging.INFO)
        LOGGER.warning("Logging-Level set to INFO")
        return "Logging-Level set to INFO"
    else:
        root.handlers[2].setLevel(logging.DEBUG)
        LOGGER.warning("Logging-Level set to DEBUG")
        return "Logging-Level set to DEBUG"


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
    failed_func_dict = {}
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
        for func, result in event.result.items():
            if (result is None or
                    (isinstance(result, bool) and result is False) or
                    (not isinstance(result, bool) and "Error: " in result)):
                failed_functions += 1
                failed_func_dict[func] = result
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
            # uptime = str(datetime.datetime.now() - boot_time).split(".")[0]
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
                      "<b>All Time:</b><br>"
                      "{:.0f} Triggers, {:.0f} Requests<br>"
                      "Processed commands: {:.0f} ({:.2f}% success)<br>"
                      "Processed functions: {:.0f} ({:.2f}% success)<br><br>"
                      "<b>Today's fails:</b> {}".format(
                          count_triggers, count_requests, count_commands,
                          success_rate_commands, count_functions,
                          success_rate_functions, count_triggers_total,
                          count_requests_total, count_commands_total,
                          success_rate_commands_total, count_functions_total,
                          success_rate_functions_total, failed_func_dict))
            logger.debug("Daily report: %s ",
                         report.replace("<br>", "\n")
                               .replace("<b>", "")
                               .replace("</b>", ""))
            tools.eventbuilder.eEvent(sender_id=name,
                                      keyword="notify.user",
                                      data={"title": "Daily report",
                                            "message": report}).trigger()
            success_functions = 0.0
            success_commands = 0.0
            failed_functions = 0.0
            failed_commands = 0.0
            count_requests = 0.0
            count_triggers = 0.0
            failed_func_dict = {}
        STATUS.task_done()


def _execute_secure(_logger, _event, _func):
    try:
        _logger.debug("[UID: %s] Executing '%s.%s'.",
                      _event.uid,
                      _func.__module__,
                      _func.__name__)
        return ["{}.{}".format(_func.__module__, _func.__name__),
                _func(key=_event.keyword, data=_event.data)]
    except Exception as e:
        _logger.exception(
            "[UID: %s] Exception in user code:", _event.uid)
        # logging.exception automatically prints the traceback!
        return ["{}.{}".format(_func.__module__, _func.__name__),
                "Error: " + str(e)]


def worker():
    """Read and process commands from the INPUT queue.

    Puts processed_results back into OUTPUT.
    """
    # Get a new logger for each thread.
    # Used instead of the global LOGGER on purpose inside this function.
    name = __name__ + "." + threading.current_thread().name
    logger = logging.getLogger(name)

    def _process(processed_event):
        input_queue = queue.Queue()
        output_queue = queue.Queue()
        queue_lock = threading.Lock()
        thread_count = 2
        thread_list = []

        def _worker():
            _name = name + "." + threading.current_thread().name
            _logger = logging.getLogger(_name)
            while True:
                queue_lock.acquire()
                if not input_queue.empty():
                    _func, _event = input_queue.get()
                    queue_lock.release()
                    output_queue.put(_execute_secure(_logger, _event, _func))
                else:
                    queue_lock.release()
                    _logger.debug("Exiting.")
                    break

        funcs = []
        processed_results = {}
        for key_substring in processed_event.parsed_kw_list:
            if key_substring in FUNC_KEYWORDS:
                for func in FUNC_KEYWORDS[key_substring]:
                    funcs.append([func["func"], processed_event])
                    # input_queue.put([func, event])

        if len(funcs) < 1:
            processed_results[name] = "Error: No matching plugin found."
        elif len(funcs) == 1:
            f_name, value = _execute_secure(logger, funcs[0][1], funcs[0][0])
            processed_results[f_name] = value
        else:
            queue_lock.acquire()
            for pair in funcs:
                input_queue.put(pair)

            for i in range(min(thread_count, input_queue.qsize())):
                t = threading.Thread(target=_worker, name="_worker%d" % i)
                t.start()
                thread_list.append(t)

            queue_lock.release()

            for t in thread_list:
                t.join()

            while not output_queue.empty():
                f_name, value = output_queue.get()
                processed_results[f_name] = value

        # processed_results = [x for x in processed_results if x]
        if not processed_results:
            processed_results[name] = "Error: No matching plugin found."

        return processed_results

    while True:
        # Wait until an item becomes available in INPUT
        logger.debug("Waiting for an item.")
        LOCK.acquire()
        event = INPUT.get()
        if event.keyword == "system.onstart":
            logger.info("The index now has %d entries.",
                        len(FUNC_KEYWORDS))
            logger.debug("%s", FUNC_KEYWORDS.keys())
            # funcs = {key: [{"name": f["name"],
            #                 "version": f["version"],
            #                 "func": str(f["func"])}
            #                for f in FUNC_KEYWORDS[key]]
            #          for key in FUNC_KEYWORDS.keys()}
            # logger.debug("%s", json.dumps(funcs, sort_keys=True, indent=4))
        else:
            LOCK.release()

        logger.debug("[UID: %s] Now processing '%s' from %s",
                     event.uid,
                     event.keyword,
                     event.sender_id)

        if event.expired:
            logger.warning(
                "[UID: %s] The event '%s' is expired and will be skipped.",
                event.uid, event.keyword)
            event.result = {
                name: "Error: The event '{}' expired and was skipped.".format(
                    event.keyword)}
        else:
            results = _process(event)
            event.result = results
            logger.info("[UID: %s] Processing of '%s' successful. "
                        "%d result%s: \n%s",
                        event.uid,
                        event.keyword,
                        len(results),
                        ("s" if len(results) > 1 else ""),
                        json.dumps(results, sort_keys=True, indent=4))

        # Put the result back into the OUTPUT queue
        if event.event_type == "request":
            OUTPUT.put(event)

        # Put the processed event into STATUS to include it in the statistics
        STATUS.put(event)

        # Let the queue know that processing is complete
        INPUT.task_done()
        if event.keyword == "system.onstart":
            LOCK.release()


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
                logger.warning("Invalid UID: %s", message.sender_id)
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
    global INPUT, OUTPUT

    LOGGER.info("Initializing...")
    INPUT = queue_in
    OUTPUT = queue_out

    # Read the number of threads to start from Samantha's config file
    # (/samantha/data/samantha.cfg)
    LOGGER.debug("Reading the config file...")
    # get the config file's path in relation to the path of this file
    this_dir = os.path.split(__file__)[0]  # ..[1] would be the filename
    if this_dir is "":
        path = "../../data"
    else:
        path = this_dir.replace("core", "data")

    config = configparser.RawConfigParser()
    config.read("{path}/samantha.cfg".format(path=path))

    try:
        # This leads to approx. X worker, X/2 sender and X/4 stat-threads.
        num_worker_threads = config.getint(__name__, "NUM_WORKER_THREADS")
    except configparser.Error:
        LOGGER.exception("Exception while reading the config:")
        num_worker_threads = 2

    num_sender_threads = int(math.ceil(1.0 * num_worker_threads / 2))
    num_statistics_threads = int(math.ceil(1.0 * num_worker_threads / 4))

    # Start the worker threads to process commands
    LOGGER.debug("Starting Worker")
    for i in range(num_worker_threads):
        thread = threading.Thread(target=worker, name="worker%d" % i)
        thread.daemon = True
        thread.start()

    # Start the sender threads to process results
    LOGGER.debug("Starting Sender")
    for i in range(num_sender_threads):
        thread = threading.Thread(target=sender, name="sender%d" % i)
        thread.daemon = True
        thread.start()

    # Start the statistics thread to process results
    LOGGER.debug("Starting Statistics-Thread")
    for i in range(num_statistics_threads):
        thread = threading.Thread(target=stats_worker, name="stats%d" % i)
        thread.daemon = True
        thread.start()

    LOGGER.info("Initialisation complete.")
    return True


def stop():
    """Stop the module."""
    global INITIALIZED

    LOGGER.info("Exiting...")
    LOGGER.warning("Waiting for INPUT to be emptied. It currently holds "
                   "%d items.", INPUT.qsize())
    INPUT.join()
    LOGGER.warning("Waiting for OUTPUT to be emptied. It currently holds "
                   "%d items.", OUTPUT.qsize())
    OUTPUT.join()
    LOGGER.warning("Waiting for STATUS to be emptied. It currently holds "
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
