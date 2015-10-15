#!/usr/bin/env python
# -*- coding: utf-8 -*-

import glob
import os
import imp

def start_interfaces(interfaces):
    #read config
    #import Interfaces according to config
    for i in interfaces:
        i.start()

def log(content, interfaces):
    print(content)
    for i in interfaces:
        i.log(content=content, interfaces=interfaces)

def import_plugins(interfaces):
    filenames = glob.glob("plugins/*_plugin.py")
    print(filenames)
    for i in range(0,len(filenames)):
        log(content="found %s" % (filenames[i]), interfaces=interfaces)
        filenames[i] = imp.load_source("plugin", filenames[i])
        if filenames[i].is_sam_plugin:
            plugins.append(filenames[i].Plugin())  #Automatically starts the plugins via __init__()
            log(content="Plugin %s imported successfully." % (f), interfaces=interfaces)
    return plugins

def output(interfaces, content):
    for i in interfaces:
        i.output(content)

def set_config(interfaces, key, value):
    #read config file
    for l in config_file:
        if key in l:
            pass
            #replace with key:value

if __name__ == "__main__":
    path = os.getcwd()
    interfaces = []
    #import interfaces
    start_interfaces(interfaces=interfaces)
    plugins = []
    plugins = import_plugins(interfaces=interfaces)
    log(content="Plugins imported", interfaces=interfaces)
    log("Interfaces started",interfaces=interfaces)

    
    
'''
def set_something(plugin_keyword, object, target_state):
    for p in plugins:
        if keyword in p.keywords and p.has_set:
            result = p.set(object, target_state)
            if result == 1
                pass
            else
                print("Error from {name}: {description}".format(name=p.name, description=result))

def get_something(plugin_keyword, object, target_state):
    for p in plugins:
        if keyword in p.keywords and p.has_set:
            result = p.set(object, target_state)
            if result == -1
                print("Error from {name}: {description}".format(name=p.name, description=result))
            else
                #process Result, could be path to a file, link, etc
                pass

def toggle_something(plugin_keyword, object):
    for p in plugins:
        if keyword in p.keywords and p.has_toggle:
            result = p.toggle(object)
            if result == 1
                pass
            else
                print("Error from {name}: {description}".format(name=p.name, description=result))
'''