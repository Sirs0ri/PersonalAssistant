#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import core

is_sam_interface = 1
name = "Commandline Interface"

def log(content):
    print("[info] " + content)

def initialize():
    print("Hello!")
    while True:
        print("Please enter a command!")
        command = raw_input("")
        if "exit" == command:
            sys.exit()
        else:
            print(core.get_answer(command))