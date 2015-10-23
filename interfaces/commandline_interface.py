#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, urllib
from daemon import Daemon
#import core

is_sam_interface = 0
name = "Commandline"

class Interface(Daemon):

    def log(self, content):
        print("[info] " + content)
    
    def get_answer(self, command, keyword=None, parameter=None):
        command = urllib.urlencode({"command":command})
        keyword = urllib.urlencode({"keyword":keyword})
        parameter = urllib.urlencode({"parameter":parameter})
        answer = urllib.urlopen("http://127.0.0.1:5000?%s&%s&%s" % (command, keyword, parameter)).read()
        if answer:
            return answer
        else:
            return "Error"
    
    def initialize(self):
        print("Hello!")
        while True:
            print("Please enter a command!")
            command = raw_input("")
            if "exit" == command:
                sys.exit()
            else:
                print(get_answer(command))
    
    def run(self):
        self.initialize()