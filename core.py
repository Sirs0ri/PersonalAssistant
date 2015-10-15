#!/usr/bin/env python
# -*- coding: utf-8 -*-

def log(interfaces, name="", content=""):
    print(name + "\t" + str(content))
    for i in interfaces:
        i.log(content)
