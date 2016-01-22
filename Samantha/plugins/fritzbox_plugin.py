#!/usr/bin/env python
# -*- coding: utf-8 -*-

import core, fritzconnection

is_sam_plugin = 0
name = "FritzBox"
keywords = ["schedule_10s"]
has_toggle = 0
has_set = 0

def dictlist_to_dictdict(the_list, key):
    """
    This takes a list of dicts and converts it to a dict of dicts. The parameter "key" specifies which key of the original dicts will be used to generate the new dict.
    
    Example:
    >>> the_list = [{"id": 1, "name": "One"}, {"id": 2, "name": "Two"}, {"id": 3, "name": "Three"}]
    >>> print the_list[2]
    {"id": 2, "name": "Two"}
    >>> the_dict = dictlist_to_dictdict(the_list, "name")
    >>> print the_dict
    {"One": {"id": 1, "name": "One"}, "Two": {"id": 2, "name": "Two"}, "Three": {"id": 3, "name": "Three"}}
    >>> print the_dict["two"]
    {"id": 2, "name": "Two"}
    """
    the_dict = {}
    try:
        for item in the_list:
            the_dict[key] = item
    except Exception:
        pass
    return the_dict
    
def initialize():
    address = "192.168.178.1"
    user = "Samantha"
    password = core.private_variables.fritzbox_password
    old_deviceslist = []
    fritzhosts = fritzconnection.FritzHosts(address, user, password)
    deviceslist = fritzhosts.get_hosts_info()
    devicesdict = dictlist_to_dictdict(deviceslist)

def process(key, params):
    try:
        if key == "onstart":
            core.log(name, ["Startup...","Hello World!"], "info")
            return {"processed": True, "value": "Success.", "plugin": name}
        elif key == "onexit":
            core.log(name, ["I'm not even running anymore!"], "logging")
            return {"processed": True, "value": "Success.", "plugin": name}
        elif key in ["test", "static"]: 
            s = "I could do sth now..."
            core.log(name, ["  " + s], "debug")
            return {"processed": True, "value": s, "plugin": name}
        else: 
            #core.log(name, ["  Illegal command.","  Key:{}".format(key),"  Parameters: {}".format(params)], "warning")
            return {"processed": False, "value": "Keyword not in use. ({}, {})".format(key, params), "plugin": name}
    except Exception as e:
        core.log(name, ["{}".format(e)], "error")
        return {"processed": False, "value": e, "plugin": name}
