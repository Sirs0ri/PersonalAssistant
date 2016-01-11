#!/usr/bin/env python
# -*- coding: utf-8 -*-

import core

is_sam_plugin = 0
name = "Test"
keywords = ["test", "static", "onstart", "onexit"]
has_toggle = 0
has_set = 0


def initialize():

def stop():

def process(key, params):
    try:
        if key == "onstart":
            core.log(name, ["Startup","Hello World!"], "info")
        elif key == "onexit":
            core.log(name, ["I'm not even running anymore!"], "logging")
        elif key in ["test", "static"]: 
            core.log(name, ["  I could do sth now"], "debug")
        else: 
            core.log(name, ["  Illegal command.","Key:{}".format(key),"Parameters: {}".format(params)], "warning")
    except Exception as e:
        core.log(name, ["{}".format(e)], "error")
