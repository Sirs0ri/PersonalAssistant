#!/usr/bin/env python
# -*- coding: utf-8 -*-

import core, sys, traceback

is_sam_plugin = 0
name = "Test"
keywords = ["test", "static", "onstart", "onexit"]
has_toggle = 0
has_set = 0

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
        print("-"*60)
        print("Exception in user code:")
        print("-"*60)
        traceback.print_exc(file=sys.stdout)
        print("-"*60)
        core.log(name, ["{}".format(e)], "error")
        return {"processed": False, "value": e, "plugin": name}
