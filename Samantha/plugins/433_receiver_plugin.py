#!/usr/bin/env python
# -*- coding: utf-8 -*-

import core, subprocess, os, threading, signal, time

is_sam_plugin = 1
name = "433_RX"
keywords = []
has_toggle = 0
has_set = 0

class Plugin_Thread(threading.Thread):

    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = name + "_Thread"
        self.process = None
        
    def run(self):
        core.log(self.name, ["      Started"], "logging")
        self.process = subprocess.Popen(["sudo", "/home/pi/Desktop/libraries/433Utils/RPi_utils/RFSniffer"], stdout=subprocess.PIPE)
        core.log(self.name, ["Subprocess started"], "logging")
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

def initialize():
    global t
    core.log(name, ["      Starting thread."], "logging")
    t.start()

def stop():
    global t
    core.log(name, ["  Exiting"], "logging")
    t.stop()
    t.join()

def process(key, params):
    core.log(name, ["  Illegal command.","Key:{}".format(key),"Parameters: {}".format(params)], "warning")