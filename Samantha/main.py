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

def import_plugins():
    """
    Function to import plugins from the /plugins folder. Valid plugins are marked by <name>.is_sam_plugin == 1.
    """
    plugins = []
    #list files in /plugin folder
    #filenames = glob.glob("plugins/*_plugin.py")
    filenames = glob.glob("plugins/*_plugin.py")
    core.log(name, "Importing Plugins: \n" + str(filenames))

    #try importing each plugin
    for i in range(0,len(filenames)):
        core.log(name, "Found %s" % (filenames[i]))
        try:
            new_plugin = imp.load_source("samplugin" + str(i), filenames[i])
            core.log(name, "%s imported successfully." % (filenames[i]))
            #Test if the imported file is a valid Plugin
            try:
                if new_plugin.is_sam_plugin:
                    plugins.append(new_plugin)
                    core.log(name, "  Name:\t\t" + new_plugin.name)
                    core.log(name, "  Keywords:\t" + str(new_plugin.keywords))
                    new_plugin.initialize()
            except AttributeError:
                core.log(name, "%s is not a valid Plugin." % (filenames[i]))
        except ImportError:
            core.log(name, "%s could not be imported successfully." % (filenames[i]))
        core.log()
    return plugins

@app.route("/")
def process():
    return "Running"

@app.route('/shutdown')
def shutdown():
    shutdown_server()
    return 'Server shutting down...'

if __name__ == "__main__":
    name = "Mainframe"
    plugins = []

    core.log(name, "Starting up!")

    
    plugins = import_plugins()
    core.log(name, plugins)

    core.log(name, "Finished.")

    app.run(host="0.0.0.0")

