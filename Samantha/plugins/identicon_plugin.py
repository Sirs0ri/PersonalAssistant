#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
plugin to create identicons
Reference: https://github.com/azaghal/pydenticon/blob/master/docs/usage.rst
Might be used to create a colored overlay over a b/w wallpaper
"""

import pydenticon, core, time, global_variables

is_sam_plugin = 1
name = "Identicon"
keywords = ["identicon"]
has_toggle = 0
has_set = 0

def generate_identicon(data="I'm Samantha", path="/data/identicon.png"):
    """
    generates an identicon and sends it to the G2
    possibly via an AutoRemote Plugin?
    """
    core.log(name, ["    Generating the Identicon...","    Data is {}".format(data)], "logging")
    generator = pydenticon.Generator(5, 5)
    identicon = generator.generate(data, 300, 300)
    core.log(name, ["    Generated the Identicon. Saving at {}...".format(global_variables.folder_base + path)], "logging")
    f = open(global_variables.folder_base + path, "wb")
    f.write(identicon)
    f.close()
    core.log(name, ["    Saved the Identicon at {}.".format(global_variables.folder_base_short + path)], "info")
    return path

def process(key, params):
    try:
        if key == "identicon":
            core.log(name, ["  Generating an Identicon with the data '{}'.".format(params)], "info")
            if params:
                result = generate_identicon(params[0])
            else:
                result = generate_identicon()
            return {"processed": True, "value": result, "plugin": name}
        else:
            #core.log(name, ["  Illegal command.","  Key:{}".format(key),"  Parameters: {}".format(params)], "warning")
            return {"processed": False, "value": "Keyword not in use. ({}, {})".format(key, params), "plugin": name}
    except Exception as e:
        core.log(name, ["{}".format(e)], "error")
        return {"processed": False, "value": e, "plugin": name}
