#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pydenticon, core, time, sys, traceback

"""
This plugin is used to create identicons (little Icons generated from a string, you might have seen them as default usericons on GitHub). It's based on the pydenticon-library (https://github.com/azaghal/pydenticon).

Reference: https://github.com/azaghal/pydenticon/blob/master/docs/usage.rst
The Idendicons are currently used to create a colored overlay over a b/w wallpaper, a later usecase might be in a GUI.
"""

is_sam_plugin = 1
name = "Identicon"
keywords = ["identicon"]
has_toggle = 0
has_set = 0

def generate_identicon(data="I'm Samantha", path="/data/identicon.png"):
    """
    This generates an identicon and saves it to th elocal storage.
    """
    core.log(name, ["    Generating the Identicon...","    Data is {}".format(data)], "logging")
    # Initialize the generator with a 5x5-patches pattern
    generator = pydenticon.Generator(5, 5)
    # Generate an Identicon with the given data and a size of 300x300px
    identicon = generator.generate(data, 300, 300)
    core.log(name, ["    Generated the Identicon. Saving at {}...".format(core.global_variables.folder_base + path)], "logging")
    f = open(core.global_variables.folder_base + path, "wb")
    f.write(identicon)
    f.close()
    core.log(name, ["    Saved the Identicon at {}.".format(core.global_variables.folder_base_short + path)], "info")
    return {"processed": True, "value": core.global_variables.folder_base + path, "plugin": name}

def process(key, params):
    try:
        if key == "identicon":
            core.log(name, ["  Generating an Identicon with the data '{}'.".format(params)], "info")
            if params:
                result = generate_identicon(params[0])
            else:
                result = generate_identicon()
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
