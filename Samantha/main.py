#!/usr/bin/env python
# -*- coding: utf-8 -*-
import glob, imp, sys, threading, time, urllib, logging
from flask import Flask,request
import core

"""
This is the main part, the "core" of Samantha.
It starts a Flask-Server which is used to receive commands (via Lan or localhost) on port 5000.

"""
name = "Mainframe"

app = Flask(__name__)

restart = 1
threads = []
plugins = []
key_index = {}

def import_plugins():
    """
    Function to import plugins from the /plugins folder. Valid plugins are marked by <name>.is_sam_plugin == 1.
    """
    plugins = []
    plugin_names = []
    #list files in Samantha's /plugin folder
    core.log(name, "Importing Plugins.")
    filenames = glob.glob("/home/pi/Desktop/PersonalAssistant/Samantha/plugins/*_plugin.py")
    core.log(name, "  {} possible plugins found.".format(len(filenames)))

    #try importing each plugin
    for i in range(0,len(filenames)):
        core.log(name, "  Found {}".format(filenames[i]))
        try:
            new_plugin = imp.load_source("samplugin{}".format(i), filenames[i])
            core.log(name, "    Successfully imported {}.".format(filenames[i]))
            #Test if the imported file is a valid Plugin
            if new_plugin.is_sam_plugin:
                #add it to the list of plugins
                plugins.append(new_plugin)
                core.log(name, "    Name: {}\tKeywords: {}".format(new_plugin.name, new_plugin.keywords))
                #initialize the plugin
                new_plugin.initialize()
                core.log(name, "    {} initialized successfully".format(new_plugin.name, new_plugin.keywords))
            else: 
                #is_sam_plugin == 0 -> the plugin is not supposed to be imported.
                core.log(name, "   {} is not a valid Plugin (no error).".format(filenames[i]))
        except ImportError:
            core.log(name, "  Error: {} wasn't imported successfully.".format(filenames[i]))
        except AttributeError:
            core.log(name, "  Error: {} is not a valid Plugin.".format(filenames[i]))
    for p in plugins:
        plugin_names.append(p.name)
    core.log(name, "Imported plugins: {}".format(plugin_names))
    return plugins

def generate_index():
    """
    Generates and returns an index of keywords and the plugins that react to them.
    Exmple: key_index = {"344":[<433-Plugin>], "light":[<433-plugin>, <LED-Plugin>], "led":[<LED-Plugin>]}
    """
    global plugins
    key_index = {}
    core.log(name, "Indexing Keywords")
    for p in plugins:
        for k in p.keywords:
            try:
                key_index[k].append(p)
            except KeyError:    #key isn't indexed yet
                key_index[k] = []
                key_index[k].append(p)
                core.log(name, "  Created new Key: '{}'".format(k))
    core.log(name, "  Indexed Keywords: {}".format(key_index))
    return key_index

@app.route("/")
def process():
    """
    Process the data received via Flask
    Accesses the parameters "Keyword", "Parameter" and "Command"
    """
    global plugins
    #get parameters
    key = request.args.get('key')
    param = request.args.get('param')
    comm = request.args.get('comm')
    core.log("Incoming", "Keyword {}, Parameter {}, Command {}".format(key,param,comm))
    #process the command
    processed = 0
    for p in plugins:
        if key in p.keywords:
            processed = 1
            core.log(name, "  The plugin {} matches the keyword.".format(p.name))

            p.process(key, param, comm)
    if not processed:
        core.log(name, "  No matching Plugin found.")
    return "Processing\nKeyword {}\nParameter {}\nCommand {}".format(key,param,comm)

@app.route('/shutdown/')
def shutdown():
    """
    Shuts down first the Flask-Server, then every Thread started by the main module and all the plugins.
    """
    core.log(name, "Received the request to shut down.")
    func = request.environ.get("werkzeug.server.shutdown")
    if func is None:
        raise RuntimeError("Not running with the Werkzeug Server")
    func()
    core.log(name, " Flask stopped successfully. Waiting for plugins to stop.")
    for t in threads + plugins:
        t.stop()
    core.log(name, " Plugins stopped.")
    return 'Server shutting down...'

@app.route('/restart/')
def restart():
    """
    Restart the complete program. It'll shutdown Flask and set the Restart-Flag back to 1 so that main() will be executed again after it's completed (aka after Flask and the Plugins are shut down correctly.) 
    """
    global restart
    core.log(name, "Received the request to restart.")
    restart = 1
    # this will cause main() to restart itself after the server's shut down.
    shutdown()
    return 'Server restarting...'

def main():
    """
    This is the main function. 
    It starts everything and does stuff.
    """
    global plugins
    global key_index
    global app
    global restart
    core.log(name,"\n  ____    _    __  __    _    _   _ _____ _   _    _     \n / ___|  / \  |  \/  |  / \  | \ | |_   _| | | |  / \    \n \___ \ / _ \ | |\/| | / _ \ |  \| | | | | |_| | / _ \   \n  ___) / ___ \| |  | |/ ___ \| |\  | | | |  _  |/ ___ \  \n |____/_/   \_\_|  |_/_/   \_\_| \_| |_| |_| |_/_/   \_\ \n                                                     hi~")
    core.log(name, "Starting up!")
    
    restart = 0
    plugins = import_plugins()
    key_index = generate_index()
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
    core.log(name,"See you next mission!\n  ____    _    __  __    _    _   _ _____ _   _    _     \n / ___|  / \  |  \/  |  / \  | \ | |_   _| | | |  / \    \n \___ \ / _ \ | |\/| | / _ \ |  \| | | | | |_| | / _ \   \n  ___) / ___ \| |  | |/ ___ \| |\  | | | |  _  |/ ___ \  \n |____/_/   \_\_|  |_/_/   \_\_| \_| |_| |_| |_/_/   \_\ \n                                                    bye~")