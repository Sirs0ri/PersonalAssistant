#!/usr/bin/env python
# -*- coding: utf-8 -*-
import glob, imp
from flask import Flask,request
import core

app = Flask(__name__)


def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

def load_interfaces():
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
                    d = new_interface.Interface(pidfile="/tmp/Samantha_Interface_%s.pid" % new_interface.name)
                    d.start()
                    interfaces.append(d)
                    core.log(interfaces, name, "  Name:\t\t" + new_interface.name)
            except AttributeError:
                core.log(interfaces, name, "%s is not a valid Interface." % (filenames[i]))
        except ImportError:
            core.log(interfaces, name, "%s could not be imported successfully." % (filenames[i]))
    return interfaces

def stop_interfaces(interfaces):
    """
    kills all interface-daemons
    """
    for i in interfaces:
        i.stop()

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

@app.route("/")
def process():
    return "works."

@app.route('/shutdown', methods=['POST'])
def shutdown():
    shutdown_server()
    return 'Server shutting down...'

if __name__ == "__main__":
    name = "Mainframe"
    interfaces = []
    plugins = []
    
    core.log(interfaces, name, "Starting up!")
    
    interfaces = load_interfaces()
    core.log(interfaces, name, interfaces)
    plugins = import_plugins(interfaces)
    core.log(interfaces, name, plugins)

    core.log(interfaces, name, "Finished.")
    
    app.run()
    
    stop_interfaces(interfaces)

    
    
    
    
    