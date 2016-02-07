#!/usr/bin/env python
# -*- coding: utf-8 -*-

import core, subprocess, os, threading, signal, time, sys, traceback

"""
This plugin starts a tool ("RFSniffer) that reads the data from a receiver for 433MHz signals connected to pin 27.
The original source can be found at https://github.com/ninjablocks/433Utils, I modified it so that it sends a message to Flask whenever it reveived a command. 

It's designed as a thread instide a thread to allow me to check when the sniffer has actally shut down.
"""

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
        # Start the actual Sniffer as a Subprocess.
        self.process = subprocess.Popen(["sudo", core.global_variables.folder_base + "/tools/433Utils/RPi_utils/RFSniffer"], stdout=subprocess.PIPE)
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
            # force-stop the sniffer
            t.stop()
            # Wait for it to end. As soon as the process has ended, `self.process.poll()` in line 30 will return the sniffer's return-code which will then stop the containing thread which again will be registered by join().
            t.join()
            return {"processed": True, "value": "Thread Exited", "plugin": name}
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
