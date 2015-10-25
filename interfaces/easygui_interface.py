#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, easygui
import core
from .daemon import Daemon

is_sam_interface = 1
name = "Easygui"

class Interface(Daemon):

    def log(content):
        easygui.msgbox(content)

    def run():
        while True:
            command=easygui.enterbox(title="W.I.L.L.", msg="Please enter a command")
            if command=="exit":
                sys.exit()
            elif command==None:
                sys.exit()
            else:
                core.get_answer(command)
                easygui.msgbox(answer)

def create(pidfile):
    d = Interface(pidfile)
    return d