#!/usr/bin/env python
# -*- coding: utf-8 -*-

import core, fritzconnection, sys, traceback

"""
This plugin implements the API of my router, a "FritzBox" (https://avm.de/produkte/fritzbox/). 
Currently it triggers events if a new device connects to the router and if a known device (dis-)connects.

Later usecases could be muting a phone placed in my bedroom during the night, opening ports, managing the NAS' shares and sending a Fax.

The plugin is based on the fritzconnection-library (https://bitbucket.org/kbr/fritzconnection/)
"""

is_sam_plugin = 1
name = "FritzBox"
keywords = ["onstart","schedule_10s"]
has_toggle = 0
has_set = 0

if is_sam_plugin:
    devicesdict = {}
    old_cached_devicesdict = {}
    fritzhosts = None

def initialize():
    global fritzhosts
    global devicesdict
    global old_cached_devicesdict
    # establish a new connection via the FritzHosts-module
    fritzhosts = fritzconnection.FritzHosts(address="192.168.178.1", user="Samantha", password=core.private_variables.fritzbox_password)
    deviceslist = fritzhosts.get_hosts_info()
    devicesdict = { i["mac"]: i for i in deviceslist }
    old_cached_devicesdict = devicesdict
    for device in sorted(deviceslist, key=lambda item:item["status"]):  # I'm not comparing anything here, so it doesn't matter if i use the list or dict.
        if device["status"] == "1":
            core.process(key="device_online", params=[device["name"], device["mac"], device["ip"]], origin=name, target="all", type="trigger")
        else:
            core.process(key="device_offline", params=[device["name"], device["mac"], device["ip"]], origin=name, target="all", type="trigger")
    return {"processed": True, "value": "Success. Initialized {} devices.".format(len(deviceslist)), "plugin": name}

def update_devices():
    global devicesdict
    global old_cached_devicesdict
    global fritzhosts
    deviceslist = fritzhosts.get_hosts_info()
    #ignored_macs = ["00:80:77:F2:71:23"]    # this list holds the mac-addresses of ignored devices. They won't be able to trigger events such as coming on/offline or registering. The 1st listed address is for example my printer which dis- and reconnects every few minutes and only spams my logs.
    ignored_macs = []
    # trasnform the list into a dict to be able to compare the entries (via a device's mac-address as unique key)
    cached_devicesdict = { i["mac"]: i for i in deviceslist if i["mac"] not in ignored_macs}
    updated = 0
    new = 0
    for key in cached_devicesdict:
        if key in old_cached_devicesdict and key in devicesdict:
            if cached_devicesdict[key]["status"] == old_cached_devicesdict[key]["status"] and not cached_devicesdict[key]["status"] == devicesdict[key]["status"]:
                #This will be triggered if a device's status hasn't changed since the last scan, but doesn't match the global deviceslist. A device's status isn't changed immedeately to ignore short disconnects
                devicesdict[key]["status"] = cached_devicesdict[key]["status"]
                updated += 1
                if devicesdict[key]["status"] == "1":
                    core.process(key="device_online", params=[devicesdict[key]["name"], devicesdict[key]["mac"], devicesdict[key]["ip"]], origin=name, target="all", type="trigger")
                else:
                    core.process(key="device_offline", params=[devicesdict[key]["name"], devicesdict[key]["mac"], devicesdict[key]["ip"]], origin=name, target="all", type="trigger")
        else:
            core.log(name, ["New Device:","Key: {}".format(key),"{}".format(cached_devicesdict[key]),"In devicesdict: {}".format(key in devicesdict),"In old_cached_devicesdict: {}".format(key in old_cached_devicesdict)], "info")
            devicesdict[key] = cached_devicesdict[key]
            core.process(key="device_new", params=[cached_devicesdict[key]["name"], cached_devicesdict[key]["mac"], cached_devicesdict[key]["ip"]], origin=name, target="all", type="trigger")
            new += 1
    old_cached_devicesdict = cached_devicesdict
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
        print("-"*60)
        print("Exception in user code:")
        print("-"*60)
        traceback.print_exc(file=sys.stdout)
        print("-"*60)
        core.log(name, ["{}".format(e)], "error")
        return {"processed": False, "value": e, "plugin": name}
