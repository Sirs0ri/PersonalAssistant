#!/usr/bin/env python
# -*- coding: utf-8 -*-

import core, threading, time

is_sam_plugin = 1
name = "Schedule_Plugin"
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
        i = 0
        while self.running:
            core.get_answer("schedule", i, "schedule {}".format(i % 60))
            i += 5
            time.sleep(300)
        core.log(self.name, "Not running anymore.")
        
    def stop(self):
        self.running = 0
        core.log(self.name, "Exited")
        
t = Plugin_Thread(name)

def initialize():
    global t
    core.log(name, "Starting")
    t.start()

def stop():
    global t
    core.log(name, "Exiting")
    t.stop()