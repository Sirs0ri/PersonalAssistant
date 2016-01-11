#!/usr/bin/env python
# -*- coding: utf-8 -*-

import core, subprocess, os, threading, signal, time

is_sam_plugin = 1
name = "433_TX"
keywords = ["433", "light"]
has_toggle = 0
has_set = 0

def send(scode, dcode, state):
    subprocess.call(["sudo", "/home/pi/Desktop/libraries/433Utils/RPi_utils/send", scode, dcode, state], stdout=subprocess.PIPE)
    #time.sleep(0.1)
    core.log(name, ["  Code {} {} {} sent successfully.".format(scode, dcode, state)], "info")

def process(key, params):
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
    try:
        core.log(name, ["  Processing: {}, {}".format(key, params)], "info")
        if key == "433":
            if "4195665" in params:
                #turn on LEDs under bed
                send("11111", "1", "1")
            elif "4195668" in params:
                #turn off LEDs under bed
                send("11111", "1", "0")
            elif "4198737" in params:
                #turn on standing lamp1
                send("11111", "2", "1")
            elif "4198740" in params:
                #turn off standing lamp1
                send("11111", "2", "0")
            elif "4199505" in params:
                #turn on standing lamp2
                send("11111", "3", "1")
            elif "4199508" in params:
                #turn off standing lamp2
                send("11111", "3", "0")
            elif "4199697" in params:
                #turn ambient lights on
                #core.process(key="light", params=["on"], origin=name)
                send("11111", "1", "1")
                send("11111", "2", "0")
                send("11111", "3", "1")
            elif "4199700" in params:
                #turn all lights off
                core.process(key="light", params=["off"], origin=name)
                # send("11111", "1", "0")
                # send("11111", "2", "0")
                # send("11111", "3", "0")
            else:
                core.log(name, ["  Illegal parameter(s)."], "warning")
        elif key == "light":
            if "off" in params:
                send("11111", "1", "0")
                send("11111", "2", "0")
                send("11111", "3", "0")
            elif "on" in params:
                send("11111", "1", "1")
                send("11111", "2", "1")
                send("11111", "3", "1")
            else:
                core.log(name, ["  Illegal parameter."], "warning")
        else:
            core.log(name, ["  Illegal command."], "warning")
    except Exception as e:
        core.log(name, ["{}".format(e)], "error")