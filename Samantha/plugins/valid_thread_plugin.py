#!/usr/bin/env python
# -*- coding: utf-8 -*-

import core, threading, time, datetime

is_sam_plugin = 0
name = "Test"
keywords = ["test", "static"]
has_toggle = 0
has_set = 0

class Plugin_Thread(threading.Thread):

    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = name + "_Thread"
        self.running = 1
        
    def run(self):
        core.log(self.name, ["Started"], "logging")
        while self.running:
            time.sleep(1)
        core.log(self.name, ["Not running anymore."], "logging")
        
    def stop(self):
        self.running = 0
        core.log(self.name, ["Exited"], "info")

if is_sam_plugin:
    t = Plugin_Thread(name)

def initialize():
    global t
    core.log(name, ["Starting thread."], "logging")
    t.start()

def stop():
    global t
    core.log(name, ["Exiting"], "logging")
    t.stop()
    t.join()

def process(key, params):
    try:
        core.log(name, ["  I could do sth now"], "debug")
        pass
    except Exception as e:
        core.log(name, ["{}".format(e)], "error")