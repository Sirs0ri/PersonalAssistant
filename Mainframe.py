#!/usr/bin/env python
# -*- coding: utf-8 -*-

import glob
import os
import imp
import core

def start_interfaces(interfaces):
    #read config
    #import Interfaces according to config
    for i in interfaces:
        i.start()

def import_plugins(interfaces):
    
    core.log(interfaces)
    #list files in /plugin folder
    filenames = glob.glob("plugins/*_plugin.py")
    core.log(interfaces, name, "Importing Plugins: \n" + str(filenames))
    
    for i in range(0,len(filenames)):
        core.log(interfaces)
        core.log(interfaces, name, "Found %s" % (filenames[i]))
        #new_plugin = "samplugin" + str(i)
        try:
            new_plugin = imp.load_source("samplugin" + str(i), filenames[i])
            #import new_plugin
            core.log(interfaces, name, "%s imported successfully." % (filenames[i]))
            try:
                if new_plugin.is_sam_plugin:
                    plugins.append(new_plugin)
                    core.log(interfaces, name, "  Name:\t\t" + new_plugin.name)
                    core.log(interfaces, name, "  Keywords:\t" + str(new_plugin.keywords))
                    new_plugin.initialize(interfaces)
            except AttributeError:
                core.log(interfaces, name, "%s is not a valid Plugin." % (filenames[i]))
        except ImportError:
            core.log(interfaces, name, "%s could not be imported successfully." % (filenames[i]))
        core.log(interfaces)
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
    name = "Mainframe"
    interfaces = []
    plugins = []
    core.log(interfaces)
    core.log(interfaces, name, "Starting up!")
    path = os.getcwd()
    #import interfaces
    start_interfaces(interfaces=interfaces)
    plugins = import_plugins(interfaces=interfaces)
    core.log(interfaces, name, "Plugins imported")
    core.log(interfaces)
    core.log(interfaces, name, "Interfaces started")

    
    
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