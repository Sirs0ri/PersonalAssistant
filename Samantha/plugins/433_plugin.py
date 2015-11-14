#!/usr/bin/env python
# -*- coding: utf-8 -*-

import core, subprocess, os, threading, signal, time

is_sam_plugin = 1
name = "433MHz"
keywords = ["433", "light"]
has_toggle = 0
has_set = 0

class Plugin_Thread(threading.Thread):

    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = name + "_Thread"
        self.process = None
        
    def run(self):
        core.log(self.name, "Started")
        self.process = subprocess.Popen(["sudo", "/home/pi/Desktop/libraries/433Utils/RPi_utils/RFSniffer"], stdout=subprocess.PIPE)
        core.log(self.name, "Subprocess started")
        while True:
            if self.process.poll() is not None: 
                #Would return the process' return code once it's terminated. 
                #Will return None if the process is still running.
                break
            time.sleep(1)
        core.log(self.name, "Not running anymore.")
        
    def stop(self):
        subprocess.call(["sudo", "pkill", "RFSniffer"])
        core.log(self.name, " Exited")
        
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

def send(scode, dcode, state):
    subprocess.call(["sudo", "/home/pi/Desktop/libraries/433Utils/RPi_utils/send", scode, dcode, state], stdout=subprocess.PIPE)
    time.sleep(0.1)
    core.log(name, "  Code {} {} {} sent successfully.".format(scode, dcode, state))

def process(key, param, comm):
    """
    Funfact: this is how the Codes work:
    Dec-Code   System-Code      Device-Code      off  on
    4195665    01 00 00 00 00   00 01 01 01 01   00   01
    4195668    01 00 00 00 00   00 01 01 01 01   01   00
    4198737    01 00 00 00 00   01 00 01 01 01   00   01
    4198740    01 00 00 00 00   01 00 01 01 01   01   00
    4199505    01 00 00 00 00   01 01 00 01 01   00   01
    4199508    01 00 00 00 00   01 01 00 01 01   01   00
    4199697    01 00 00 00 00   01 01 01 00 01   00   01
    4199700    01 00 00 00 00   01 01 01 00 01   01   00
    """
    if key == "433":
        if param == "4195665":
            #turn on LEDs under bed
            send("11111", "1", "1")
        elif param == "4195668":
            #turn off LEDs under bed
            send("11111", "1", "0")
        elif param == "4198737":
            #turn on standing lamp1
            send("11111", "2", "1")
        elif param == "4198740":
            #turn off standing lamp1
            send("11111", "2", "0")
        elif param == "4199505":
            #turn on standing lamp2
            send("11111", "3", "1")
        elif param == "4199508":
            #turn off standing lamp2
            send("11111", "3", "0")
    elif key == "light":
        if param == "off":
            send("11111", "1", "0")
            send("11111", "2", "0")
            send("11111", "3", "0")
        elif param == "on":
            send("11111", "1", "1")
            send("11111", "2", "1")
            send("11111", "3", "1")