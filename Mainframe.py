#!/usr/bin/env python
import glob, os, imp

def import_plugins():
    filenames = glob.glob("/plugins/*_plugin.py")
    plugins = []
    for i in range(0,len(filenames)):
    for f in filenames:
        try:
            filenames[i] = imp.load_source("plugin", filenames[i])
            if filenames[i].is_sam_plugin:
            plugins.append(filenames[i].Plugin())  #Automatically starts the plugins via __init__()
            log("Plugin %s imported successfully." % (f))
        except: ImportError:
            log("Error while importing plugin %s" % (f))

def start_interfaces():
    interfaces = []
    #read config
    #import Interfaces according to config
    for i in interfaces:
        i.start()

def log(content):
    for i in interfaces:
        i.log(content)

def output(content):
    for i in interfaces:
        i.output(content)

def set_config(key, value):
    #read config file
    for l in config_file:
        if key in l:
            #replace with key:value

if __name__ == "__main__":
    path = os.getcwd()
    import_plugins()
    start_interfaces()
    log("Plugins imported")
    log("Interfaces started")

    
    
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