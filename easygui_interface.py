#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, easygui, time
import core
from daemon import Daemon

is_sam_interface = 1
name = "Easygui"

class Interface(Daemon):

    def __init__(self, pidfile, stdin="/dev/null", stdout="/dev/null", stderr="/dev/null", interfaces=[]):
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.pidfile = pidfile
        self.interfaces = interfaces
        core.log(self.interfaces, name, "Created myself.")

    def log(self, content):
        easygui.msgbox(content)

    def run(self):
        core.log(self.interfaces, name, "Started myself.")
        while True:
            command=easygui.enterbox(title="W.I.L.L.", msg="Please enter a command")
            if command=="exit":
                sys.exit()
            elif command==None:
                sys.exit()
            else:
                core.get_answer(command)
                easygui.msgbox(answer)


def create(interfaces, pidfile):
    core.log(interfaces, name, "Starting up. " + pidfile)
    d = Interface(pidfile)
    core.log(interfaces, name, "Created the daemon.")
    d.start()
    core.log(interfaces, name, "Started the daemon.")
    return d