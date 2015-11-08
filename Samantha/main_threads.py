#!/usr/bin/env python
# -*- coding: utf-8 -*-
import glob, imp, sys, threading, time, urllib
from flask import Flask,request
import core

name = "Mainframe"

app = Flask(__name__)


threads = []
plugins = []

class flask_thread (threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.name = "Flask_Thread"
    def run(self):
        global app
        core.log(self.name, "Starting")
        app.debug = True
        app.run(host="0.0.0.0")
        core.log(self.name, "Exiting")
    def stop(self):
        urllib.urlopen("http://127.0.0.1:5000/shutdown")

def import_plugins():
    """
    Function to import plugins from the /plugins folder. Valid plugins are marked by <name>.is_sam_plugin == 1.
    """
    plugins = []
    #list files in /plugin folder
    core.log(name, "Importing Plugins.")
    filenames = glob.glob("plugins/*_plugin.py")
    core.log(name, "{} possible plugins found.".format(len(filenames)))

    #try importing each plugin
    for i in range(0,len(filenames)):
        core.log(name, "Found {}".format(filenames[i]))
        try:
            new_plugin = imp.load_source("samplugin{}".format(i), filenames[i])
            core.log(name, "{} imported successfully.".format(filenames[i]))
            #Test if the imported file is a valid Plugin
            try:
                if new_plugin.is_sam_plugin:
                    plugins.append(new_plugin)
                    core.log(name, "  Name:\t{}\n  Keywords:\t{}".format(new_plugin.name, new_plugin.keywords))
                    new_plugin.initialize()
            except AttributeError:
                core.log(name, "{} is not a valid Plugin.".format(filenames[i]))
        except ImportError:
            core.log(name, "{} wasn't imported successfully.".format(filenames[i]))
    return plugins

@app.route("/")
def process():
    core.log(
        name, "Keyword {key}, Parameter {param}, Command {comm}".format(
            key=request.args.get('key', ''), 
            param=request.args.get('param', ''), 
            comm=request.args.get('comm', '')
            )
        )
    return "Running"

@app.route('/shutdown')
def shutdown():
    func = request.environ.get("werkzeug.server.shutdown")
    if func is None:
        raise RuntimeError("Not running with the Werkzeug Server")
    func()
    for t in threads + plugins:
        t.stop()
    core.log(name, "Shutdown completed.")
    return 'Server shutting down...'
'''
@app.route('/restart')
def restart():
    shutdown_server()
    main()
    return 'Server restarting...'
'''
def main():
    global plugins
    core.log(name, "Starting up!")
    t = flask_thread()
    t.start()
    threads.append(t)
    plugins = import_plugins()
    core.log(name, "Startup finished.")
    
    

if __name__ == "__main__":
    main()

