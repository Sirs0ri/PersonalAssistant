#!/usr/bin/env python
# -*- coding: utf-8 -*-

import core

is_sam_plugin = 1
name = "Test_Plugin"
keywords = ["test", "demo"]
has_toggle = 0
has_set = 0
interfaces = []

def initialize(i):
    interfaces = i
    core.log(interfaces)
    core.log(interfaces, name, "Startup")
    core.log(interfaces, name, "I could do sth now")
    core.log(interfaces, name, "Hello World!")