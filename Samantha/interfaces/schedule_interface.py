#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import core
from daemon import Daemon

is_sam_interface = 1
name = "Schedule"

class Interface(Daemon):

    def __init__(self, pidfile, stdin="/dev/null", stdout="/dev/null", stderr="/dev/null", interfaces=[]):
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.pidfile = pidfile
        self.interfaces = interfaces
        core.log(self.interfaces, name, "Created myself.")

    def log(content):
        pass

    def run():
        i = 0
        while True:
            time.sleep(300)
            i += 5
            core.get_answer("schedule", "schedule {}".format(i % 60), i)