#!/usr/bin/env python
# -*- coding: utf-8 -*-

#import libraries
import glob, os, imp, time
from flask import Flask
#import Sam-related things
import core
from daemon import Daemon
import global_variables as VARS

app = Flask(__name__)

class Mainframe_Daemon(Daemon):
    
    def load_interfaces(self):
        """
        loads and starts available interfaces
        """
        
        interfaces = []
        #list files in the /interfaces folder
        filenames = glob.glob("interfaces/*_interface.py")
        core.log(interfaces, name, "Importing Interfaces: \n" + str(filenames))
    
        for i in range(0,len(filenames)):
            core.log(interfaces, name, "Found %s" % (filenames[i]))
            try:
                new_interface = imp.load_source("saminterface" + str(i), filenames[i])
                core.log(interfaces, name, "%s imported successfully." % (filenames[i]))
                #Test if the imported file is a valid Plugin
                try:
                    if new_interface.is_sam_interface:
                        interfaces.append(new_interface)
                        core.log(interfaces, name, "  Name:\t\t" + new_interface.name)
                        new_interface.initialize()
                except AttributeError:
                    core.log(interfaces, name, "%s is not a valid Interface." % (filenames[i]))
            except ImportError:
                core.log(interfaces, name, "%s could not be imported successfully." % (filenames[i]))
        return interfaces
        
    def import_plugins(interfaces):
        """
        Function to import plugins from the /plugins folder. Valid plugins are marked by <name>.is_sam_plugin == 1.
        """
        plugins = []
        #list files in /plugin folder
        filenames = glob.glob("plugins/*_plugin.py")
        core.log(interfaces, name, "Importing Plugins: \n" + str(filenames))
    
        #try importing each plugin
        for i in range(0,len(filenames)):
            core.log(interfaces, name, "Found %s" % (filenames[i]))
            try:
                new_plugin = imp.load_source("samplugin" + str(i), filenames[i])
                core.log(interfaces, name, "%s imported successfully." % (filenames[i]))
                #Test if the imported file is a valid Plugin
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

    def run(self):
        '''
        name = "Mainframe_Daemon"
        interfaces = []
        plugins = []
        
        interfaces = load_interfaces()
        plugins = import_plugins()
        '''
        while 1:
            time.sleep(1)


    def process(self):
        return "klappt."

    def get_interfaces(self):
        return interfaces
        
    def get_plugins(self):
        return plugins


'''
#Do I still need this?
def output(interfaces, content):
    for i in interfaces:
        i.output(content)

def set_config(interfaces, key, value):
    #read config file
    for l in config_file:
        if key in l:
            pass
            #replace with key:value
'''


@app.route("/")
def respond():
    #return("I received your request.")
    return(daemon.process())

if __name__ == "__main__":
    name = "Mainframe"
    interfaces = []
    plugins = []
    daemon = Mainframe_Daemon(pidfile="/tmp/MainframeDaemon.pid")
    print("running")
    daemon.start()
    print("daemon started")
    app.run()
    print("Flask started")

#    interfaces = daemon.get_interfaces()
#    plugins = daemon.get_plugins()

    interfaces = daemon.get_interfaces()
    daemon.get_interfaces()
    plugins = daemon.get_plugins()
    daemon.get_plugins()
    
    core.log(interfaces, name, "Starting up!")
    core.log(interfaces, name, daemon)

    #core.log(interfaces, name, interfaces)
    #core.log(interfaces, name, plugins)

    #import interfaces
    #interfaces = load_interfaces()
    #import plugins
    #plugins = import_plugins(interfaces=interfaces)

    #core.log(interfaces, name, "Plugins imported")
    #core.log(interfaces, name, "Interfaces started")



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