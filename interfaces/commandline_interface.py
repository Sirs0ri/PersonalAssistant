#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, urllib
#import core

is_sam_interface = 0
name = "Commandline Interface"

def log(content):
    print("[info] " + content)

def get_answer(command, keyword=None, parameter=None):
    command = urllib.urlencode({"command":command})
    keyword = urllib.urlencode({"keyword":keyword})
    parameter = urllib.urlencode({"parameter":parameter})
    answer = urllib.urlopen("http://127.0.0.1:5000?%s&%s&%s" % (command, keyword, parameter)).read()
    if answer:
        return answer
    else:
        return "Error"

def initialize():
    print("Hello!")
    while True:
        print("Please enter a command!")
        command = raw_input("")
        if "exit" == command:
            sys.exit()
        else:
            print(get_answer(command))

if __name__ == '__main__':
    initialize()