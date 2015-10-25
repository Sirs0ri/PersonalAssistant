#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib, datetime

#def log(interfaces, name="", content=""):
def log(name="", content=""):
    
    #print to the script calling .log(); usually Mainframe.py
    print(str(datetime.datetime.now()) + "\n" + name + "\t" + str(content))
    print
    '''
    #log in file
    logfile=open("log.txt", 'r+')
    logfile.write(str(datetime.datetime.now()) + "\n\t" + name + "\t" + str(content))
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

if __name__ == "__main__":
    print("This file is meant to be implemented by Samantha's Mainframe!")