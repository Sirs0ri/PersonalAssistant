#!/usr/bin/env python
# -*- coding: utf-8 -*-

import core

is_sam_plugin = 0
name = "Test"
keywords = ["test", "static"]
has_toggle = 0
has_set = 0


def initialize():
    core.log(name, "Startup")
    core.log(name, "I could do sth now")
    core.log(name, "Hello World!")

def stop():
    core.log(name, "I'm not even running anymore!")