#!/usr/bin/env python
# -*- coding: utf-8 -*-

import core, sys, traceback, pychromecast

"""
This plugin demonstrates how a normal plugin is built. 
It can't do nothing fancy, and won't be loaded by default.
"""

is_sam_plugin = 1
name = "Chromecast"
keywords = ["schedule_10s"]
has_toggle = 0
has_set = 0

if is_sam_plugin:
    player_status = False
    cast = pychromecast.get_chromecast(friendly_name="Chromecast_Max")
    if cast:
        mc = cast.media_controller
    else:
        core.log(name, ["Chromeast not found!"], "error")
        mc = None

def update_device():
    if mc:
        if not mc.status.player_status == player_status:
            player_status = mc.status.player_status
            if player_status == "PLAYING":
                core.process(key="light", params=["ambient"], origin=name, target="all", type="trigger")
            else:
                core.process(key="light", params=["normal"], origin=name, target="all", type="trigger")
            return {"processed": True, "value": "Status updated to: '{}'".format(player_status), "plugin": name}
        else:
            return {"processed": True, "value": "None", "plugin": name}
    else:
        return {"processed": False, "value": "Chromecast not available!", "plugin": name}

def process(key, params):
    try:
        if key == "schedule_10s": 
            result = update_device()
            return result
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
