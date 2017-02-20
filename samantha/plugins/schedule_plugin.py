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
import logging
import random
import threading
import time

# related third party imports

# application specific imports
import samantha.context as context
from samantha.core import subscribe_to
from samantha.plugins.plugin import Plugin
from samantha.tools import eventbuilder


__version__ = "1.3.17"


# Initialize the logger
LOGGER = logging.getLogger(__name__)

SUNRISE = datetime.datetime(1970, 1, 1)
SUNSET = datetime.datetime(1970, 1, 1)

PLUGIN = Plugin("Schedule", True, LOGGER, __file__)


def worker():
    """Check if events should be triggered, sleep 1sec, repeat."""
    name = __name__ + ".Thread"
    logger = logging.getLogger(name)
    logger.debug("Started.")

    def _check_daytime(_datetime_obj, _timelist):
        if (SUNSET < SUNRISE < _datetime_obj or
                SUNRISE < _datetime_obj < SUNSET or
                _datetime_obj < SUNSET < SUNRISE):
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
            eventbuilder.eEvent(sender_id=name,
                                keyword=keyword,
                                data=_timelist).trigger()

        # calculate time between now and sunrise
        if SUNRISE < _datetime_obj:
            # the sunrise is in the past
            sunrise_pre_post = "post"
            diff_sunrise = _datetime_obj - SUNRISE
        else:
            # the sunrise is in the future
            sunrise_pre_post = "pre"
            diff_sunrise = SUNRISE - _datetime_obj
        if 0 < diff_sunrise.seconds % 300 < 59:
            # the difference between now and the sunrise is a multiple of 5
            # minutes (this check is executed every minute, thus I'm checking
            # this in a way that the condition becomes true every 5th minute.
            keyword_sunrise = "time.sunrise.{}.{}".format(
                sunrise_pre_post,
                diff_sunrise.seconds / 60)
            LOGGER.warning("Triggering event '%s'!", keyword_sunrise)
            eventbuilder.eEvent(sender_id=name,
                                keyword=keyword_sunrise,
                                data=_timelist).trigger()

        # calculate time between now and sunset
        if SUNSET < _datetime_obj:
            # the sunset is in the past
            sunset_pre_post = "post"
            diff_sunset = _datetime_obj - SUNSET
        else:
            # the sunset is in the future
            sunset_pre_post = "pre"
            diff_sunset = SUNSET - _datetime_obj
        if 0 < diff_sunset.seconds % 300 < 59:
            # the difference between now and the sunset is a multiple of 5
            # minutes (this check is executed every minute, thus I'm checking
            # this in a way that the condition becomes true every 5th minute.
            keyword_sunset = "time.sunset.{}.{}".format(
                sunset_pre_post,
                diff_sunset.seconds / 60)
            LOGGER.warning("Triggering event '%s'!", keyword_sunset)
            eventbuilder.eEvent(sender_id=name,
                                keyword=keyword_sunset,
                                data=_timelist).trigger()

        logger.debug("SUNRISE: %s, SUNSET: %s, NOW: %s",
                     SUNRISE, SUNSET, _datetime_obj)

    def _trigger(keyword, data):
        if "10s" in keyword:
            ttl = 8
        elif "10s" in keyword:
            ttl = 55
        elif "10s" in keyword:
            ttl = 3300
        else:
            ttl = 0

        eventbuilder.eEvent(sender_id=name,
                            keyword=keyword,
                            data=data,
                            ttl=ttl).trigger()

    # Initialize the two random events.
    # They'll be triggered randomly once an hour/once a day. These two counters
    # count down the seconds until the next event. They'll be reset to a random
    # value every hour (day) between 0 and the number of seconds in an hour/day
    # The default values are 120secs for the hourly event and 180 for the daily
    # so that the two events are being triggered relatively soon after starting
    rnd_hourly_counter = 120
    rnd_daily_counter = 180

    while True:
        datetime_obj = datetime.datetime.now()
        timetuple = datetime_obj.timetuple()
        """
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
        """
        timelist = list(timetuple)
        if rnd_hourly_counter == 0:
            _trigger(keyword="time.schedule.hourly_rnd", data=timelist)
        if rnd_daily_counter == 0:
            _trigger(keyword="time.schedule.daily_rnd", data=timelist)
        rnd_hourly_counter -= 1
        rnd_daily_counter -= 1
        if timelist[5] in [0, 10, 20, 30, 40, 50]:
            _trigger(keyword="time.schedule.10s", data=timelist)
            if timelist[5] == 0:
                # Seconds = 0 -> New Minute
                _trigger(keyword="time.schedule.min", data=timelist)
                # Check for a change in the time of day
                _check_daytime(datetime_obj, timelist)
                if timelist[4] == 0:
                    # Minutes = 0 -> New Hour
                    _trigger(keyword="time.schedule.hour", data=timelist)
                    rnd_hourly_counter = random.randint(0, 3599)
                    if timelist[3] == 0:
                        # Hours = 0 -> New Day
                        _trigger(keyword="time.schedule.day", data=timelist)
                        rnd_daily_counter = random.randint(0, 86399)
                        if timelist[2] == 1:
                            # Day of Month = 1 -> New Month
                            _trigger(keyword="time.schedule.mon",
                                     data=timelist)
                            if timelist[1] == 1:
                                # Month = 1 -> New Year
                                _trigger(keyword="time.schedule.year",
                                         data=timelist)
        # sleep to take work from the CPU
        time.sleep(1)


@subscribe_to("system.onstart")
def start_thread(key, data):
    """Set up the plugin by starting the worker-thread."""
    thread = threading.Thread(target=worker)
    thread.daemon = True
    thread.start()
    return "Worker started successfully."


@subscribe_to("weather.sys.update")
def sun_times(key, data):
    """Update the times for sunset and -rise."""
    global SUNRISE, SUNSET
    result = ""
    invalid = True
    if "sunrise" in data:
        invalid = False
        sunrise = datetime.datetime.fromtimestamp(data["sunrise"])
        if SUNRISE is not sunrise:
            SUNRISE = sunrise
            LOGGER.debug("Updated Sunrise to %s",
                         SUNRISE.strftime('%Y-%m-%d %H:%M:%S'))
            result += "Sunrise updated successfully."
    if "sunset" in data:
        invalid = False
        sunset = datetime.datetime.fromtimestamp(data["sunset"])
        if SUNSET is not sunset:
            SUNSET = sunset
            LOGGER.debug("Updated Sunset to %s",
                         SUNSET.strftime('%Y-%m-%d %H:%M:%S'))
            result += "Sunset updated successfully."
    if invalid:
        result = "Error: The data does not contain info about sunrise/-set."
    if result == "":
        result = "Sunrise/-set were already up to date."
    return result
