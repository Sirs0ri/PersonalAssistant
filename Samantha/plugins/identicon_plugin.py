#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
plugin to create identicons
Reference: https://github.com/azaghal/pydenticon/blob/master/docs/usage.rst
Might be used to create a colored overlay over a b/w wallpaper
"""

import pydenticon, core, time, global_variables

is_sam_plugin = 0
name = "Identicon"
keywords = ["identicon", "schedule_h"]
has_toggle = 0
has_set = 0

def generate_identicon(data="I'm Samantha"):
    """
    generates an identicon and sends it to the G2
    possibly via an AutoRemote Plugin?
    """
    generator = pydenticon.Generator(5, 5)
    identicon = generator.generate(data, 200, 200)
    f = open(global_variables.folder_base + "/data/identicon.png", "wb")
    f.write(identicon)
    f.close()
    # Send image to phone

def initialize():
    core.log(name, ["Everything's fine."], "logging")

def stop():
    core.log(name, ["I'm not even running anymore!"], "logging")
    
def process(key, params):
    try:
        if key == "identicon":
            core.log(name, ["  Generating an Identicon with the data '{}'.".format(params[0])], "info")
            if params:
                generate_identicon(params[0])
            else:
                generate_identicon()
        elif key == "schedule_h":
            if "0" in params:
                generate_identicon(time.time())
            else:
                core.log(name, ["  Illegal parameter."], "warning")
        else:
            core.log(name, ["  Illegal command."], "warning")
    except Exception as e:
        core.log(name, ["{}".format(e)], "error")