#!/usr/bin/env python
# -*- coding: utf-8 -*-

import core, subprocess, os, threading, signal

is_sam_plugin = 1
name = "433MHz"
keywords = ["433"]
has_toggle = 0
has_set = 0

class Plugin_Thread(threading.Thread):

    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = name + "_Thread"
        self.process = None
        
    def run(self):
        core.log(self.name, "Started")
        #self.process = subprocess.Popen("/home/pi/Desktop/PersonalAssistant/Samantha/plugins/433_plugin.sh", stdout=subprocess.PIPE)
        self.process = subprocess.Popen("/home/pi/Desktop/libraries/433Utils/RPi_utils/RFSniffer", stdout=subprocess.PIPE, bufsize=1)
        for line in iter(self.process.stdout.read(1), b''):
            print line,
        core.log(self.name, "Subprocess started")
        while True:
            core.log(self.name, "Getting Output.")
            output = self.process.stdout.read(1)
            core.log(self.name, "Got Output.")
            if output == '' and self.process.poll() is not None:
                break
            if output:
                core.log(name, output.strip())
            core.log(self.name, "Processed Output.")
        core.log(self.name, "Not running anymore.")
        
    def stop(self):
        os.kill(self.process.pid, signal.SIGTERM)
        core.log(self.name, "Exited")
        
if is_sam_plugin:
    t = Plugin_Thread(name)

def initialize():
    global t
    core.log(name, "Starting thread.")
    t.start()

def stop():
    global t
    core.log(name, "Exiting")
    t.stop()
    t.join()