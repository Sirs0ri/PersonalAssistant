#!/usr/bin/env python
# -*- coding: utf-8 -*-

import core, sys, traceback, pychromecast

"""
This plugin demonstrates how a normal plugin is built. 
It can't do nothing fancy, and won't be loaded by default.
"""

is_sam_plugin = 1
name = "Chromecast"
keywords = ["onstart", "schedule_10s"]
has_toggle = 0
has_set = 0

if is_sam_plugin:
    player_state = False
    content_type = False
    cast = None
    mc = None

def initialize():
    global cast
    global mc
    cast = pychromecast.get_chromecast(friendly_name="Chromecast_Max")
    if cast:
        mc = cast.media_controller
        if mc:
            return {"processed": True, "value": "Initialization successfull.", "plugin": name}
        else:
            return {"processed": False, "value": "Connection to Mediacontroller wasn't successfull", "plugin": name}
    else:
        return: {"processed": False, "value": "Chromeast not found!", "plugin": name}

def update_device():
    global player_state
    global content_type
    if mc:
        if not mc.status.player_state == player_state or not mc.status.content_type == content_type:
            player_state = mc.status.player_state
            content_type = mc.status.content_type
            if player_state == "PLAYING" and "audio" not in content_type:
                core.process(key="light", params=["ambient"], origin=name, target="all", type="trigger")
            else:
                core.process(key="light", params=["normal"], origin=name, target="all", type="trigger")
            return {"processed": True, "value": "Status updated to: '{}' ({})".format(player_state, content_type), "plugin": name}
        else:
            return {"processed": True, "value": "None", "plugin": name}
    else:
        return {"processed": False, "value": "Chromecast not available!", "plugin": name}

def process(key, params):
    try:
        if key == "onstart":
            result = initialize()
            return result
        elif key == "schedule_10s": 
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
