#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
plugin to create identicons
Reference: https://github.com/azaghal/pydenticon/blob/master/docs/usage.rst
Might be used to create a colored overlay over a b/w wallpaper
"""

import pydenticon, core

is_sam_plugin = 0
name = "Identicon"
keywords = ["identicon"]
has_toggle = 0
has_set = 0

def main():
    """
    generates an identicon and sends it to the G2
    possibly via an AutoRemote Plugin?
    """
    generator = pydenticon.Generator(5, 5)
    identicon = generator.generate("john.doe@example.com", 200, 200)
    f = open("sample.png", "wb")
    f.write(identicon)
    f.close()
    # Send image to phone

def initialize():
    core.log(name, "Everything's fine.")