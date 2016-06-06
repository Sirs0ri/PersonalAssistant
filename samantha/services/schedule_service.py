"""
This plugin triggers schedules events. the different commands are triggered:
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
# TODO: [ ] docstrings
# TODO: [ ] comments
#
###############################################################################


import datetime
import threading
import time
import traceback


import logging
from services.service import BaseClass
import tools


# Initialize the logger
LOGGER = logging.getLogger(__name__)


class PluginThread(threading.Thread):

    def __init__(self, name):
        super(PluginThread, self).__init__()
        self.LOGGER = logging.getLogger(__name__ + ".Thread")
        self.name = name + "_T"
        self.running = 1

    def run(self):
        LOGGER.debug("Started.")
        # initialisation
        while self.running == 1:
            timetuple = datetime.datetime.now().timetuple()
            """
            value: time.struct_time(tm_year=2016, tm_mon=1, tm_mday=22,
                                    tm_hour=11, tm_min=26, tm_sec=13,
                                    tm_wday=4, tm_yday=22, tm_isdst=-1)
                0: tm_year=2016
                1: tm_mon=1
                2: tm_mday=22
                3: tm_hour=11
                4: tm_min=26
                5: tm_sec=13
                6: tm_wday=4
                7: tm_yday=22
                8: tm_isdst=-1
            """
            timelist = list(timetuple)
            if timelist[5] in [0, 10, 20, 30, 40, 50]:
                tools.eventbuilder.Event(sender_id=self.name,
                                         keyword="schedule_10s",
                                         data=timelist).trigger()
                if timelist[5] == 0:
                    # Seconds = 0 -> New Minute
                    tools.eventbuilder.Event(sender_id=self.name,
                                             keyword="schedule_min",
                                             data=timelist).trigger()
                    if timelist[4] == 0:
                        # Minutes = 0 -> New Hour
                        tools.eventbuilder.Event(sender_id=self.name,
                                                 keyword="schedule_hour",
                                                 data=timelist).trigger()
                        if timelist[3] == 0:
                            # Hours = 0 -> New Day
                            tools.eventbuilder.Event(sender_id=self.name,
                                                     keyword="schedule_day",
                                                     data=timelist).trigger()
                            if timelist[2] == 1:
                                # Day of Month = 1 -> New Month
                                tools.eventbuilder.Event(
                                    sender_id=self.name,
                                    keyword="schedule_mon",
                                    data=timelist).trigger()
                                if timelist[1] == 1:
                                    # Month = 1 -> New Year
                                    tools.eventbuilder.Event(
                                        sender_id=self.name,
                                        keyword="schedule_year",
                                        data=timelist).trigger()
            # sleep to take work from the CPU
            time.sleep(1)
        LOGGER.debug("Not running anymore.")

    def stop(self):
        self.running = 0
        LOGGER.debug("Exited.")


class Service(BaseClass):

    def __init__(self, uid):
        LOGGER.debug("Initializing...")
        self.name = "Schedule"
        self.uid = uid
        self.keywords = ["onstart", "onexit"]
        self.t = PluginThread(uid)
        super(Service, self).__init__(logger=LOGGER, file_path=__file__)

    def stop(self):
        LOGGER.debug("I'm not doing shit anymore.")
        super(Service, self).stop()

    def process(self, key, data=None):
        try:
            if key == "onstart":
                LOGGER.debug("Starting thread...")
                self.t.start()
                return {"processed": True, "value": "Success.", "plugin": self.name}
            elif key == "onexit":
                LOGGER.debug("Exiting...")
                self.t.stop()
                self.t.join()
                return {"processed": True, "value": "Success.", "plugin": self.name}
            else:
                return {"processed": False, "value": "Keyword not in use. ({}, {})".format(key, data), "plugin": self.name}
        except Exception as e:
            LOGGER.error("Exception in user code:\n%s", traceback.format_exc())

            return {"processed": False, "value": e, "plugin": self.name}
