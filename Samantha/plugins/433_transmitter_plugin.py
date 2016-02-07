#!/usr/bin/env python
# -*- coding: utf-8 -*-

import core, subprocess, os, threading, signal, time, sys, traceback

"""
This plugin uses the 433Utils library (https://github.com/ninjablocks/433Utils) to send signals via a 433MHz transmitter connected to the RasPi.
"""

is_sam_plugin = 1
name = "433_TX"
keywords = ["433", "light"]
has_toggle = 0
has_set = 0

def send(scode, dcode, state):
    """
    This method sends the commands via the aforementioned tool included in the 433Utils library. It requires a systemcode (00000-11111), a devicecode (1-4) and a state (0/1 for off and on)
    """
    subprocess.call(["sudo", core.global_variables.folder_base + "/tools/433Utils/RPi_utils/send", scode, dcode, state], stdout=subprocess.PIPE)
    #time.sleep(0.1)
    core.log(name, ["  Code {} {} {} sent successfully.".format(scode, dcode, state)], "info")

def process(key, params):
    """
    The received codes are transmittes via 'params'. They are a decimal expression of the original binary codes received by the system. 00 in the code means 'True' (-> AND), 01 means 'False':
    
    Dec-Code   System-Code      Device-Code      off  on
    4195665    01 00 00 00 00   00 01 01 01 01   00   01
    4195668    01 00 00 00 00   00 01 01 01 01   01   00
    4198737    01 00 00 00 00   01 00 01 01 01   00   01
    4198740    01 00 00 00 00   01 00 01 01 01   01   00
    4199505    01 00 00 00 00   01 01 00 01 01   00   01
    4199508    01 00 00 00 00   01 01 00 01 01   01   00
    4199697    01 00 00 00 00   01 01 01 00 01   00   01
    4199700    01 00 00 00 00   01 01 01 00 01   01   00
    
    That means: If the receiver reads the code '4195665', that means that the original signal was meant to 
        * turn off (the two off-bits are identical) 
        * the first device (1st pair of digits in the devicecode is 00, the other 5 are 01. For the 2nd device only the 2nd pair of the devicecode's digits would be '00') 
        * in the set of devices with systemcode 01111 (on my remote that means that all but the 1st switches are in the up-position)
    """
    try:
        core.log(name, ["  Processing: {}, {}".format(key, params)], "info")
        if key == "433":
            if "4195665" in params:
                #turn on LEDs under bed
                send("11111", "1", "1")
                return {"processed": True, "value": "Success.", "plugin": name}
            elif "4195668" in params:
                #turn off LEDs under bed
                send("11111", "1", "0")
                return {"processed": True, "value": "Success.", "plugin": name}
            elif "4198737" in params:
                #turn on standing lamp1
                send("11111", "2", "1")
                return {"processed": True, "value": "Success.", "plugin": name}
            elif "4198740" in params:
                #turn off standing lamp1
                send("11111", "2", "0")
                return {"processed": True, "value": "Success.", "plugin": name}
            elif "4199505" in params:
                #turn on standing lamp2
                send("11111", "3", "1")
                return {"processed": True, "value": "Success.", "plugin": name}
            elif "4199508" in params:
                #turn off standing lamp2
                send("11111", "3", "0")
                return {"processed": True, "value": "Success.", "plugin": name}
            elif "4199697" in params:
                #turn ambient lights on
                result = core.process(key="light", params=["ambient"], origin=name, target="all", type="trigger")
                return {"processed": True, "value": result, "plugin": name}
            elif "4199700" in params:
                #turn all lights off
                result = core.process(key="light", params=["off"], origin=name, target="all", type="trigger")
                return {"processed": True, "value": result, "plugin": name}
            else:
                return {"processed": False, "value": "Parameter not in use. ({}, {})".format(key, params), "plugin": name}
        elif key == "light":
            if "off" in params:
                send("11111", "1", "0")
                send("11111", "2", "0")
                send("11111", "3", "0")
                return {"processed": True, "value": "All lights turned off successfully.", "plugin": name}
            elif "on" in params:
                send("11111", "1", "1")
                send("11111", "2", "1")
                send("11111", "3", "1")
                return {"processed": True, "value": "Success.", "plugin": name}
            elif "ambient" in params:
                send("11111", "1", "1")
                send("11111", "3", "1")
                send("11111", "2", "0")
                return {"processed": True, "value": "Success.", "plugin": name}
            elif "normal" in params:
                send("11111", "2", "1")
                send("11111", "1", "0")
                send("11111", "3", "0")
                return {"processed": True, "value": "Success.", "plugin": name}
            else:
                return {"processed": False, "value": "Parameter not in use. ({}, {})".format(key, params), "plugin": name}
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
