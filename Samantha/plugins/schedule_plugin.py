#!/usr/bin/env python
# -*- coding: utf-8 -*-

import core, threading, time

is_sam_plugin = 1
name = "Schedule"
keywords = []
has_toggle = 0
has_set = 0

class Plugin_Thread(threading.Thread):

    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = name + "_Thread"
        self.running = 1
        
    def run(self):
        core.log(self.name, "Started")
        starttime=time.time()
        i = 0
        self.old_hour = None
        while self.running:
            core.get_answer("schedule_min", i, "schedule_min {}".format(i % 60))
            i += 5
            self.hour = int(time.strftime("%H", time.localtime()))
            if not self.hour == self.old_hour:
                core.get_answer("schedule_h", self.hour)
                self.old_hour = self.hour
            time.sleep(30.0 - ((time.time() - starttime) % 30.0))
        core.log(self.name, "Not running anymore.")
        
    def stop(self):
        self.running = 0
        core.log(self.name, "Exited")

if is_sam_plugin:
    t = Plugin_Thread(name)

def initialize():
    global t
    core.log(name, "Starting")
    t.start()

def stop():
    global t
    core.log(name, "Exiting")
    t.stop()