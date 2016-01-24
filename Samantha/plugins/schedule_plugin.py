#!/usr/bin/env python
# -*- coding: utf-8 -*-

import core, threading, time, datetime

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
        # 
        # 
        # self.old_year = None
        # self.old_mon = None
        # self.old_day = None
        # self.old_hour = None
        # self.old_min = None
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
                core.process(key="schedule_10s", params=timelist, origin=name)
                if timelist[5] == 0:
                    # Seconds = 0 -> New Minute
                    core.process(key="schedule_min", params=timelist, origin=name)
                    if timelist[4] == 0:
                        # Minutes = 0 -> New Hour
                        core.process(key="schedule_hour", params=timelist, origin=name)
                        if timelist[3] == 0:
                            # Hours = 0 -> New Day
                            core.process(key="schedule_day", params=timelist, origin=name)
                            if timelist[2] == 1:
                                # Day of Month = 1 -> New Month
                                core.process(key="schedule_mon", params=timelist, origin=name)
                                if timelist[1] == 1:
                                    # Month = 1 -> New Year
                                    core.process(key="schedule_year", params=timelist, origin=name)
            '''
            if timelist[5] in [0,10,20,30,40,50]:
                core.process(key="schedule_10s", params=timelist, origin=name)
                if timelist[5] == 0 and not timelist[4] == self.old_min:
                    core.process(key="schedule_min", params=timelist, origin=name)
                    self.old_min = timelist[4]
                    if timelist[4] == 0 and not timelist[3] == self.old_hour:
                        core.process(key="schedule_hour", params=timelist, origin=name)
                        self.old_hour = timelist[3]
                        if timelist[3] == 0 and not timelist[8] == self.old_day:
                            core.process(key="schedule_day", params=timelist, origin=name)
                            self.old_day = timelist[8]
                            if timelist[8] == 0 and not timelist[1] == self.old_mon:
                                core.process(key="schedule_mon", params=timelist, origin=name)
                                self.old_month = timelist[5]
                                if not timelist[1] == self.old_year:
                                    core.process(key="schedule_year", params=timelist, origin=name)
                                    self.old_year = timelist[1]
            '''
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
            #core.log(name, ["  Illegal command.","  Key:{}".format(key),"  Parameters: {}".format(params)], "warning")
            return {"processed": False, "value": "Keyword not in use. ({}, {})".format(key, params), "plugin": name}
    except Exception as e:
        core.log(name, ["{}".format(e)], "error")
        return {"processed": False, "value": e, "plugin": name}
