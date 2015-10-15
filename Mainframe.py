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

def log(interfaces, content=""):
    print(content)
    for i in interfaces:
        i.log(content)

def import_plugins(interfaces):
    
    log(interfaces)
    #list files in /plugin folder
    filenames = glob.glob("plugins/*_plugin.py")
    log(interfaces, "Importing Plugins: \n" + str(filenames))
    
    for i in range(0,len(filenames)):
        log(interfaces)
        log(interfaces, "Found %s" % (filenames[i]))
        new_plugin = "samplugin" + str(i)
        #filenames[i] = imp.load_source("samplugin", filenames[i])
        #imp.load_source(new_plugin, filenames[i])
        try:
            new_plugin = imp.load_source(new_plugin, filenames[i])
            #import new_plugin
            log(interfaces,"%s imported successfully." % (filenames[i]))
            try:
                if new_plugin.is_sam_plugin:
                    plugins.append(new_plugin)  #Automatically starts the plugins via __init__()
                    log(interfaces, "%s imported successfully as a Plugin." % (new_plugin.name))
            except AttributeError:
                log(interfaces, "%s is not a valid Plugin." % (filenames[i]))
        except ImportError:
            log(interfaces, "%s could not be imported successfully." % (filenames[i]))
        log(interfaces)
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
    interfaces = []
    plugins = []
    log(interfaces)
    log(interfaces, "Starting up!")
    path = os.getcwd()
    #import interfaces
    start_interfaces(interfaces=interfaces)
    plugins = import_plugins(interfaces=interfaces)
    log(interfaces, "Plugins imported")
    log(interfaces,"Interfaces started")

    
    
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