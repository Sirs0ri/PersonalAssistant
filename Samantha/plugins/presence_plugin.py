#!/usr/bin/env python
# -*- coding: utf-8 -*-

import core

is_sam_plugin = 1
name = "Test"
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
        core.log(name, ["{}".format(e)], "error")
        return {"processed": False, "value": e, "plugin": name}
