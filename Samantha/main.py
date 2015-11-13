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
    key_index = {}
    #list files in /plugin folder
    core.log(name, " Importing Plugins.")
    filenames = glob.glob("/home/pi/Desktop/PersonalAssistant/Samantha/plugins/*_plugin.py")
    core.log(name, "  {} possible plugins found.".format(len(filenames)))

    #try importing each plugin
    for i in range(0,len(filenames)):
        core.log(name, "  Found {}".format(filenames[i]))
        try:
            new_plugin = imp.load_source("samplugin{}".format(i), filenames[i])
            core.log(name, "   {} imported successfully.".format(filenames[i]))
            #Test if the imported file is a valid Plugin
            if new_plugin.is_sam_plugin:
                #add it to the list of plugins
                plugins.append(new_plugin)
                core.log(name, "    Name: {}\tKeywords: {}".format(new_plugin.name, new_plugin.keywords))
                #add the plugin's keywords to the index
                for k in new_plugin.keywords:
                    if not key_index[k]:
                        key_index[k] = []
                    key_index[k].append(new_plugin)
                new_plugin.initialize()
            else: 
                core.log(name, "    {} is not a valid Plugin (no error).".format(filenames[i]))
        except ImportError:
            core.log(name, "   {} wasn't imported successfully. Error.".format(filenames[i]))
        except AttributeError:
            core.log(name, "   {} is not a valid Plugin. Error.".format(filenames[i]))
    return plugins

@app.route("/")
def process():
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
            core.log(name, " The plugin {} matches the keyword.".format(p.name))
            '''
            try:
                p.process(key, param, comm)
            except:
                core.log(name, "ERROR: {} couldn't process the command {}|{}|{}.".format(p.name, key, param, comm))
            '''
            p.process(key, param, comm)
    if not processed:
        core.log(name, " No matching Plugin found.")
    return "Processing\nKeyword {}\nParameter {}\nCommand {}".format(key,param,comm)

@app.route('/shutdown/')
def shutdown():
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
    global restart
    core.log(name, "Received the request to restart.")
    restart = 1
    # this will cause main() to restart itself after the server's shut down.
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
    plugin_names = []
    for p in plugins:
        plugin_names.append(p.name)
    core.log(name, "Startup finished.")
    core.log(name, " Imported plugins: {}".format(plugin_names))
    
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