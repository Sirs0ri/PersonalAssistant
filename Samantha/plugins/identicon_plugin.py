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
    core.log(name, "Everything's fine.")

def stop():
    core.log(name, "I'm not even running anymore!")
    
def process(key, param, comm):
    if key == "identicon":
        core.log(name, "  Generating an Identicon with the data '{}'.".format(param))
        if param:
            generate_identicon(param)
        else:
            generate_identicon()
    elif key == "schedule_h":
        if param == "0":
            generate_identicon(time.time())
        else:
            core.log(name, "  Error: illegal parameter.")
    else:
        core.log(name, "  Error: illegal command.")