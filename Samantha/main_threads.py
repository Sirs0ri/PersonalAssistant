#!/usr/bin/env python
# -*- coding: utf-8 -*-
import glob, imp, sys, threading, time, urllib, logging
from flask import Flask,request
import core

name = "Mainframe"

app = Flask(__name__)

restart = 1
threads = []
plugins = []

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
                    core.log(name, "  Name: {}\tKeywords: {}".format(new_plugin.name, new_plugin.keywords))
                    new_plugin.initialize()
                else: 
                    core.log(name, "{} is not a valid Plugin (no error).".format(filenames[i]))
            except AttributeError:
                core.log(name, "{} is not a valid Plugin (error).".format(filenames[i]))
        except ImportError:
            core.log(name, "{} wasn't imported successfully.".format(filenames[i]))
    return plugins

@app.route("/")
def process():
    core.log(name, "Keyword {key}, Parameter {param}, Command {comm}".format(key=request.args.get('key'),param=request.args.get('param'),comm=request.args.get('comm')))
    return "Processing\nKeyword {key}\nParameter {param}\nCommand {comm}".format(key=request.args.get('key'),param=request.args.get('param'),comm=request.args.get('comm'))

@app.route('/shutdown/')
def shutdown():
    core.log(name, "Received the request to shut down.")
    func = request.environ.get("werkzeug.server.shutdown")
    if func is None:
        raise RuntimeError("Not running with the Werkzeug Server")
    func()
    core.log(name, "Shutdown completed. Waiting for plugins to stop.")
    for t in threads + plugins:
        t.stop()
    core.log(name, "Plugins stopped.")
    return 'Server shutting down...'

@app.route('/restart/')
def restart():
    global restart
    core.log(name, "Received the request to restart.")
    restart = 1
    shutdown()
    return 'Server restarting...'

def main():
    global plugins
    global app
    global restart
    core.log(name,"\n  ____    _    __  __    _    _   _ _____ _   _    _     \n / ___|  / \  |  \/  |  / \  | \ | |_   _| | | |  / \    \n \___ \ / _ \ | |\/| | / _ \ |  \| | | | | |_| | / _ \   \n  ___) / ___ \| |  | |/ ___ \| |\  | | | |  _  |/ ___ \  \n |____/_/   \_\_|  |_/_/   \_\_| \_| |_| |_| |_/_/   \_\ \n                                                     hi~")
    core.log(name, "Starting up!")
    
    restart = 0
    plugins = import_plugins()
    core.log(name, "Startup finished.")
    
    #don't log "INFO"-messages from Flask/werkzeug
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.WARNING)
    
    #app.debug = True
    core.log(name, "Starting Flask")
    app.run(host="0.0.0.0")
    
    #this'll be executed when Flask stops.
    core.log(name, "Flask shut down successfully")

if __name__ == "__main__":
    while restart:
        main()
    core.log(name, "See you next mission!")
    core.log(name, "\n- - - \ Y / - - -")