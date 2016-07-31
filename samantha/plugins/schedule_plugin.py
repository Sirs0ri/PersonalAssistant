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
import context
from core import subscribe_to
import logging
from plugins.plugin import Plugin
from tools import eventbuilder


__version__ = "1.3.7"


# Initialize the logger
LOGGER = logging.getLogger(__name__)

SUNRISE = datetime.datetime.fromtimestamp(0)
SUNSET = datetime.datetime.fromtimestamp(0)

PLUGIN = Plugin("Schedule", True, LOGGER, __file__)


def worker():
    """Check if events should be triggered, sleep 1sec, repeat."""
    name = __name__ + ".Thread"
    logger = logging.getLogger(name)
    logger.debug("Started.")

    def _check_daytime(datetime_obj, timelist):
        if (SUNSET < SUNRISE < datetime_obj or
                SUNRISE < datetime_obj < SUNSET or
                datetime_obj < SUNSET < SUNRISE):
            # The sun has risen.
            time_of_day = "day"
        else:
            # The sun hasn't risen yet.
            time_of_day = "night"

        if time_of_day == context.get_value("time.time_of_day", None):
            logger.debug("It's still %stime.", time_of_day)
        else:
            logger.debug("It's now %stime.", time_of_day)
            context.set_property("time.time_of_day", time_of_day)
            keyword = "time.time_of_day.{}".format(time_of_day)
            eventbuilder.Event(sender_id=name,
                               keyword=keyword,
                               data=timelist).trigger()

    # Initialisation
    while True:
        datetime_obj = datetime.datetime.now()
        timetuple = datetime_obj.timetuple()
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
                               keyword="time.schedule.10s",
                               data=timelist,
                               ttl=5).trigger()
            if timelist[5] == 0:
                # Seconds = 0 -> New Minute
                eventbuilder.Event(sender_id=name,
                                   keyword="time.schedule.min",
                                   data=timelist,
                                   ttl=55).trigger()
                # Check for a change in the time of day
                _check_daytime(datetime_obj, timelist)
                if timelist[4] == 0:
                    # Minutes = 0 -> New Hour
                    eventbuilder.Event(sender_id=name,
                                       keyword="time.schedule.hour",
                                       data=timelist,
                                       ttl=3300).trigger()
                    if timelist[3] == 0:
                        # Hours = 0 -> New Day
                        eventbuilder.Event(sender_id=name,
                                           keyword="time.schedule.day",
                                           data=timelist).trigger()
                        if timelist[2] == 1:
                            # Day of Month = 1 -> New Month
                            eventbuilder.Event(sender_id=name,
                                               keyword="time.schedule.mon",
                                               data=timelist).trigger()
                            if timelist[1] == 1:
                                # Month = 1 -> New Year
                                eventbuilder.Event(
                                    sender_id=name,
                                    keyword="time.schedule.year",
                                    data=timelist).trigger()
        # sleep to take work from the CPU
        time.sleep(1)


@subscribe_to("system.onstart")
def start_thread(key, data):
    """Set up the plugin by starting the worker-thread."""
    thread = threading.Thread(target=worker)
    thread.daemon = True
    thread.start()


@subscribe_to("weather.update")
def sun_times(key, data):
    """Update the times for sunset and -rise."""
    global SUNRISE, SUNSET
    success = False
    if "sys" in data:
        sunrise = datetime.datetime.fromtimestamp(data["sys"]["sunrise"])
        sunset = datetime.datetime.fromtimestamp(data["sys"]["sunset"])
        if SUNRISE is not sunrise:
            SUNRISE = sunrise
            LOGGER.debug("Updated Sunrise to %s",
                         SUNRISE.strftime('%Y-%m-%d %H:%M:%S'))
            success = True
        if SUNSET is not sunset:
            SUNSET = sunset
            LOGGER.debug("Updated Sunset to %s",
                         SUNSET.strftime('%Y-%m-%d %H:%M:%S'))
            success = True
    return success
