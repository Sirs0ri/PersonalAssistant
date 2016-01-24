#!/usr/bin/env python
# -*- coding: utf-8 -*-

import core, fritzconnection

is_sam_plugin = 1
name = "FritzBox"
keywords = ["onstart","schedule_10s"]
has_toggle = 0
has_set = 0

if is_sam_plugin:
    old_devicesdict = {}
    fritzhosts = None

def initialize():
    global fritzhosts
    global old_devicesdict
    address = "192.168.178.1"
    user = "Samantha"
    password = core.private_variables.fritzbox_password
    fritzhosts = fritzconnection.FritzHosts(address=address, user=user, password=password)
    deviceslist = fritzhosts.get_hosts_info()
    old_devicesdict = { i["mac"]: i for i in deviceslist }
    for device in deviceslist:  # I'm not comparing anything here, so it doesn't matter if i use the list or dict.
        if device["status"] == "1":
            core.process(key="device_online", params=[device["name"]], origin=name, target="all", type="trigger")
        else:
            core.process(key="device_offline", params=[device["name"]], origin=name, target="all", type="trigger")
    return {"processed": True, "value": "Success. Initialized {} devices.".format(len(deviceslist)), "plugin": name}

def update_devices():
    global old_devicesdict
    deviceslist = fritzhosts.get_hosts_info()
    devicesdict = { i["mac"]: i for i in deviceslist }
    updated = 0
    new = 0
    for key in devicesdict:
        if key in old_devicesdict:
            if not devicesdict[key]["status"] == old_devicesdict[key]["status"]:
                if devicesdict[key]["status"] == "1":
                    core.process(key="device_online", params=[devicesdict[key]["name"]], origin=name, target="all", type="trigger")
                    updated += 1
                else:
                    core.process(key="device_offline", params=[devicesdict[key]["name"]], origin=name, target="all", type="trigger")
                    updated += 1
        else:
            core.process(key="device_new", params=[devicesdict[key]["name"]], origin=name, target="all", type="trigger")
            new += 1
    old_devicesdict = devicesdict
    if updated or new:
        return {"processed": True, "value": "Updated {} devices. Found {} new devices.".format(updated, new), "plugin": name}
    else: 
        return {"processed": True, "value": "None", "plugin": name}

def process(key, params):
    try:
        if key == "onstart":
            result = initialize()
            return result
        elif key == "schedule_10s": 
            result = update_devices()
            return result
        else: 
            return {"processed": False, "value": "Keyword not in use. ({}, {})".format(key, params), "plugin": name}
    except Exception as e:
        core.log(name, ["{}".format(e)], "error")
        return {"processed": False, "value": e, "plugin": name}
