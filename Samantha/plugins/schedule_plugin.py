#!/usr/bin/env python
# -*- coding: utf-8 -*-

import core, threading, time, datetime, sys, traceback

"""
This plugin triggers schedules events. the different commands are triggered:
    * every 10 seconds
    * at the start of every minute
    * ..hour
    * ..day
    * ..month
    * ..year
All these events are triggered as soon as possible, i.e. 'Day' will be triggered at 0:00, month on the 1st at 0:00, etc.
"""

is_sam_plugin = 1
name = "Schedule"
keywords = ["onstart", "onexit"]
has_toggle = 0
has_set = 0

class Plugin_Thread(threading.Thread):

    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = name + "_T"
        self.running = 1
        
    def run(self):
        core.log(self.name, ["      Started."], "logging")
        # #initialisation
        while self.running == 1:
            timetuple = datetime.datetime.now().timetuple()
            """
            value: time.struct_time(tm_year=2016, tm_mon=1, tm_mday=22, tm_hour=11, tm_min=26, tm_sec=13, tm_wday=4, tm_yday=22, tm_isdst=-1)
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
            if timelist[5] in [0,10,20,30,40,50]:
                core.process(key="schedule_10s", params=timelist, origin=name, type="trigger")
                if timelist[5] == 0:
                    # Seconds = 0 -> New Minute
                    core.process(key="schedule_min", params=timelist, origin=name, type="trigger")
                    if timelist[4] == 0:
                        # Minutes = 0 -> New Hour
                        core.process(key="schedule_hour", params=timelist, origin=name, type="trigger")
                        if timelist[3] == 0:
                            # Hours = 0 -> New Day
                            core.process(key="schedule_day", params=timelist, origin=name, type="trigger")
                            if timelist[2] == 1:
                                # Day of Month = 1 -> New Month
                                core.process(key="schedule_mon", params=timelist, origin=name, type="trigger")
                                if timelist[1] == 1:
                                    # Month = 1 -> New Year
                                    core.process(key="schedule_year", params=timelist, origin=name, type="trigger")
            #sleep to take work from the CPU
            time.sleep(1)
        core.log(self.name, ["  Not running anymore."], "logging")
        
    def stop(self):
        self.running = 0
        core.log(self.name, ["  Exited."], "logging")

if is_sam_plugin:
    t = Plugin_Thread(name)

def process(key, params):
    global t
    try:
        if key == "onstart":
            core.log(name, ["      Starting thread..."], "logging")
            t.start()
            return {"processed": True, "value": "Success.", "plugin": name}
        elif key == "onexit":
            core.log(name, ["  Exiting.."], "logging")
            t.stop()
            t.join()
            return {"processed": True, "value": "Success.", "plugin": name}
        else: 
            return {"processed": False, "value": "Keyword not in use. ({}, {})".format(key, params), "plugin": name}
    except Exception as e:
        print("-"*60)
        print("Exception in user code:")
        print("-"*60)
        traceback.print_exc(file=sys.stdout)
        print("-"*60)
        core.log(name, ["{}".format(e)], "error")
        return {"processed": False, "value": e, "plugin": name}
