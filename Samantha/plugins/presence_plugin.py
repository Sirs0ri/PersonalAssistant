#!/usr/bin/env python
# -*- coding: utf-8 -*-

import core, sys, traceback

"""
This plugin is supposed to manage which devices are present where.
At the moment it's not doing much. Further usecases could be triggering profiles depending on who's where or whatever. ^^
"""
is_sam_plugin = 1
name = "Presence"
keywords = ["device_online", "device_offline", "device_new"]
has_toggle = 0
has_set = 0

def process(key, params):
    try:
        if key == "device_online":
            return {"processed": True, "value": "Device {} now online".format(params), "plugin": name}
        elif key == "device_offline":
            return {"processed": True, "value": "Device {} now offline".format(params), "plugin": name}
        elif key == "device_new":
            return {"processed": True, "value": "New Device: {}".format(params), "plugin": name}
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
