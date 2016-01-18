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
        #initialisation
        nexttime=time.time()
        i = 0
        delay = 5
        self.old_hour = None
        while self.running == 1:
            core.process(key="schedule_min", params=[str(i), "schedule_min {}".format(i % 60)], origin=name)
            i += 5
            nexttime += 300
            while time.time() < nexttime and self.running == 1:
                #check if the hour has changed
                self.hour = datetime.datetime.now().hour
                if not self.hour == self.old_hour:
                    core.process(key="schedule_h", params=[str(self.hour)], origin=name, target="all")
                    self.old_hour = self.hour
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
