#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib, datetime

#def log(interfaces, name="", content=""):
def log(name="", content=""):
    
    #print to the script calling .log(); usually Mainframe.py
    s = "{name} \t {content} \n  {time}".format(name=name, content=content, time=datetime.datetime.now())
    print(s)
    print
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