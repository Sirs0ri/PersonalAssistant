"""This plugin triggers schedules events.

The different commands are triggered:
    * every 10 seconds
    * at the start of every minute
    * ..hour
    * ..day
    * ..month
    * ..year

All these events are triggered as soon as possible, i.e. 'Day' will be
triggered at 0:00, month on the 1st at 0:00, etc.
"""

###############################################################################
#
# TODO: [ ]
#
###############################################################################


# standard library imports
import datetime
import threading
import time

# related third party imports

# application specific imports
# pylint: disable=import-error
from core import subscribe_to
import logging
from services.service import BaseClass
from tools import eventbuilder
# pylint: enable=import-error


__version__ = "1.2.3"


# Initialize the logger
LOGGER = logging.getLogger(__name__)

SERVICE = BaseClass("Schedule", True, LOGGER, __file__)


def worker():
    """Check if events should be triggered, sleep 1sec, repeat."""
    name = __name__ + ".Thread"
    logger = logging.getLogger(name)
    logger.debug("Started.")
    # Initialisation
    while True:
        timetuple = datetime.datetime.now().timetuple()
        # value: time.struct_time(tm_year=2016, tm_mon=1, tm_mday=22,
        #                         tm_hour=11, tm_min=26, tm_sec=13,
        #                         tm_wday=4, tm_yday=22, tm_isdst=-1)
        # ..[0]: tm_year = 2016
        # ..[1]: tm_mon = 1
        # ..[2]: tm_mday = 22
        # ..[3]: tm_hour = 11
        # ..[4]: tm_min = 26
        # ..[5]: tm_sec = 13
        # ..[6]: tm_wday = 4
        # ..[7]: tm_yday = 22
        # ..[8]: tm_isdst = -1
        timelist = list(timetuple)
        if timelist[5] in [0, 10, 20, 30, 40, 50]:
            eventbuilder.Event(sender_id=name,
                               keyword="schedule_10s",
                               data=timelist).trigger()
            if timelist[5] == 0:
                # Seconds = 0 -> New Minute
                eventbuilder.Event(sender_id=name,
                                   keyword="schedule_min",
                                   data=timelist).trigger()
                if timelist[4] == 0:
                    # Minutes = 0 -> New Hour
                    eventbuilder.Event(sender_id=name,
                                       keyword="schedule_hour",
                                       data=timelist).trigger()
                    if timelist[3] == 0:
                        # Hours = 0 -> New Day
                        eventbuilder.Event(sender_id=name,
                                           keyword="schedule_day",
                                           data=timelist).trigger()
                        if timelist[2] == 1:
                            # Day of Month = 1 -> New Month
                            eventbuilder.Event(sender_id=name,
                                               keyword="schedule_mon",
                                               data=timelist).trigger()
                            if timelist[1] == 1:
                                # Month = 1 -> New Year
                                eventbuilder.Event(sender_id=name,
                                                   keyword="schedule_year",
                                                   data=timelist).trigger()
        # sleep to take work from the CPU
        time.sleep(1)


@subscribe_to("onstart")
def start_thread(key, data):
    thread = threading.Thread(target=worker)
    thread.daemon = True
    thread.start()
