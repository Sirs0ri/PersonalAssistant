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
        core.log(name, ["Created myself."], "logging")

    def log(self, content):
        #easygui.msgbox(content)
        pass

    def run(self):
        core.log(name, ["Started myself."], "logging")
        while True:
            command=easygui.enterbox(title="W.I.L.L.", msg="Please enter a command")
            if command=="exit":
                sys.exit()
            elif command==None:
                sys.exit()
            else:
                core.process(key="process", params=[command], origin=name)
                easygui.msgbox(answer)


def create(interfaces, pidfile):
    core.log(name, ["Starting up. " + pidfile], "logging")
    d = Interface(pidfile)
    core.log(name, ["Created the daemon."], "logging")
    d.start()
    core.log(name, ["Started the daemon."], "logging")
    return d