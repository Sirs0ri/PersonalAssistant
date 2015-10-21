#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, easygui
import core

is_sam_interface = 1
name = "Easygui Interface"

def log(content):
    easygui.msgbox(content)

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
    while True:
	command=easygui.enterbox(title="W.I.L.L.", msg="Please enter a command")
	if command=="exit":
		sys.exit()
	elif command==None:
		sys.exit()
	else:
		core.get_answer(command)
        easygui.msgbox(answer)