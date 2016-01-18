#!/usr/bin/env python
# -*- coding: utf-8 -*-

import core, subprocess, os, threading, signal, time

is_sam_plugin = 1
name = "433_RX"
keywords = ["onstart", "onexit"]
has_toggle = 0
has_set = 0

class Plugin_Thread(threading.Thread):

    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = name + "_T"
        self.process = None
        
    def run(self):
        core.log(self.name, ["      Started."], "logging")
        self.process = subprocess.Popen(["sudo", "/home/pi/Desktop/libraries/433Utils/RPi_utils/RFSniffer"], stdout=subprocess.PIPE)
        core.log(self.name, ["Subprocess started."], "logging")
        while True:
            if self.process.poll() is not None: 
                #Would return the process' return code once it's terminated. 
                #Will return None if the process is still running.
                break
            time.sleep(1)
        core.log(self.name, ["  Not running anymore."], "logging")
        
    def stop(self):
        subprocess.call(["sudo", "pkill", "RFSniffer"])
        core.log(self.name, ["  Exited"], "logging")
        
if is_sam_plugin:
    t = Plugin_Thread(name)

def process(key, params):
    global t
    try:
        if key == "onstart":
            core.log(name, ["      Starting thread."], "logging")
            t.start()
            return {"processed": True, "value": "Thread started", "plugin": name}
        elif key == "onexit":
            core.log(name, ["  Exiting..."], "logging")
            t.stop()
            t.join()
            return {"processed": True, "value": "Thread Exited", "plugin": name}
        else: 
            #core.log(name, ["  Illegal command.","  Key:{}".format(key),"  Parameters: {}".format(params)], "warning")
            return {"processed": False, "value": "Keyword not in use. ({}, {})".format(key, params), "plugin": name}
    except Exception as e:
        core.log(name, ["{}".format(e)], "error")
        return {"processed": False, "value": e, "plugin": name}
