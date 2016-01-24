#!/usr/bin/env python
# -*- coding: utf-8 -*-

import core, threading, time, datetime, sys, traceback

is_sam_plugin = 0
name = "Test"
keywords = ["test", "thread"]
has_toggle = 0
has_set = 0

class Plugin_Thread(threading.Thread):

    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = name + "_T"
        self.running = 1
        
    def run(self):
        core.log(self.name, ["Started."], "logging")
        while self.running:
            time.sleep(1)
        core.log(self.name, ["Not running anymore."], "logging")
        
    def stop(self):
        self.running = 0
        core.log(self.name, ["Exited."], "info")

if is_sam_plugin:
    t = Plugin_Thread(name)

def process(key, params):
    try:
        if key == "onstart":
            core.log(name, ["Startup...","Hello World!", "Starting thread..."], "logging")
            t.start()
            return {"processed": True, "value": "Success.", "plugin": name}
        elif key == "onexit":
            core.log(name, ["Exiting..."], "logging")
            t.stop()
            t.join()
            return {"processed": True, "value": "Success.", "plugin": name}
        elif key in ["test", "thread"]: 
            s = "I could do sth now..."
            core.log(name, ["  " + s], "debug")
            return s
        else: 
            #core.log(name, ["  Illegal command.","  Key:{}".format(key),"  Parameters: {}".format(params)], "warning")
            return {"processed": False, "value": "Keyword not in use. ({}, {})".format(key, params), "plugin": name}
    except Exception as e:
        print("-"*60)
        print("Exception in user code:")
        print("-"*60)
        traceback.print_exc(file=sys.stdout)
        print("-"*60)
        core.log(name, ["{}".format(e)], "error")
        return {"processed": False, "value": e, "plugin": name}
