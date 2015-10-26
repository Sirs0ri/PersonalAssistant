#!/usr/bin/env python
# -*- coding: utf-8 -*-

import core

is_sam_plugin = 1
name = "Test_Plugin"
keywords = ["test", "demo"]
has_toggle = 0
has_set = 0


def initialize():
    core.log()
    core.log(name, "Startup")
    core.log(name, "I could do sth now")
    core.log(name, "Hello World!")