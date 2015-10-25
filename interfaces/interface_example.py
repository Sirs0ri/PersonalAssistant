#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, time, easygui
import core
from .daemon import Daemon

is_sam_interface = 1
name = "Example"

class Interface(Daemon):

    def log(content):
        #log some content
        pass

    def run():
        while True:
            #should probably contain a loop to ask for input repeatedly
            time.sleep(1)
            