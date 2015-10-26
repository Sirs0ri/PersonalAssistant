#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib
from time import strftime, localtime

#def log(interfaces, name="", content=""):
def log(name="None", content=""):
    
    #print to the script calling .log(); usually Mainframe.py
    s = "{name}\t{time}: {content}".format(name=name, time=strftime("%H:%M:%S", localtime()), content=content)
    print(s)
    '''
    #log in file
    logfile=open("log.txt", 'r+')
    logfile.write(s)
    '''

def get_answer(command, keyword=None, parameter=None):
    command = urllib.urlencode({"command":command})
    keyword = urllib.urlencode({"keyword":keyword})
    parameter = urllib.urlencode({"parameter":parameter})
    answer = urllib.urlopen("http://127.0.0.1:5000?%s&%s&%s" % (command, keyword, parameter)).read()
    if answer:
        return answer
    else:
        return "Error"