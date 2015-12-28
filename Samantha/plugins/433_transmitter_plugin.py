#!/usr/bin/env python
# -*- coding: utf-8 -*-

import core, subprocess, os, threading, signal, time

is_sam_plugin = 1
name = "433_TX"
keywords = ["433", "light"]
has_toggle = 0
has_set = 0

def initialize():
    core.log(name, ["      I don't need to be started."])

def stop():
    core.log(name, ["  I'm not running in the Background"])

def send(scode, dcode, state):
    subprocess.call(["sudo", "/home/pi/Desktop/libraries/433Utils/RPi_utils/send", scode, dcode, state], stdout=subprocess.PIPE)
    #time.sleep(0.1)
    core.log(name, ["  Code {} {} {} sent successfully.".format(scode, dcode, state)])

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
    core.log(name, ["  Processing: {}, {}, {}".format(key, param, comm)])
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
        elif param == "4199697":
            #turn ambient lights on
            #core.get_answer("light", "on")
            send("11111", "1", "1")
            send("11111", "2", "0")
            send("11111", "3", "1")
        elif param == "4199700":
            #turn all lights off
            #core.get_answer("light", "off")
            send("11111", "1", "0")
            send("11111", "2", "0")
            send("11111", "3", "0")
        else:
            core.log(name, ["  Error: illegal parameter."])
    elif key == "light":
        if param == "off":
            send("11111", "1", "0")
            send("11111", "2", "0")
            send("11111", "3", "0")
        elif param == "on":
            send("11111", "1", "1")
            send("11111", "2", "1")
            send("11111", "3", "1")
        else:
            core.log(name, ["  Error: illegal parameter."])
    else:
        core.log(name, ["  Error: illegal command."])