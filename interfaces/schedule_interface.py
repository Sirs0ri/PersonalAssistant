#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import core
from ..daemon import Daemon

is_sam_interface = 1
name = "Example"

class Interface(Daemon):

    def log(content):
        pass

    def run():
        i = 0
        while True:
            time.sleep(300)
            i += 5
            core.get_answer("schedule", "schedule {}".format(i % 60), i)