import logging


LOGGER = logging.getLogger(__name__)

INPUT = None
OUTPUT = None
INITIALIZED = False

LOGGER.debug("I was imported")


class Queue(object):

    def __init__(self, name):
        self.queue = []
        self.name = name

    def add(self, element):
        self.queue.append(element)

    def get_next(self):
        return next(iter(self.queue), None)


class InputQueue(Queue):

    def __init__(self):
        super(InputQueue, self).__init__("Input")


class OutputQueue(Queue):

    def __init__(self):
        super(OutputQueue, self).__init__("Output")


def _init():
    global INPUT
    global OUTPUT
    LOGGER.info("Initializing...")
    INPUT = InputQueue()
    OUTPUT = OutputQueue()
    return True


def stop():
    global INITIALIZED
    LOGGER.info("Exiting...")
    # TODO Clear the queues, Alert the user if they're not empty.
    INITIALIZED = False
    return True


def initialize():
    global INITIALIZED
    if not INITIALIZED:
        INITIALIZED = _init()
    else:
        LOGGER.info("Already initialized!")
