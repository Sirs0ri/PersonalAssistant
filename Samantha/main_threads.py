#!/usr/bin/env python
# -*- coding: utf-8 -*-
import glob, imp, sys, threading, time
from flask import Flask,request
import core

name = "Mainframe"

app = Flask(__name__)

threadID = 1
threads = []

class flask_thread (threading.Thread):
    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
    def run(self):
        global app
        print "Starting " + self.name
        app.run(host="0.0.0.0")
        print "Exiting " + self.name

def shutdown_server():
    func = request.environ.get("werkzeug.server.shutdown")
    if func is None:
        raise RuntimeError("Not running with the Werkzeug Server")
    func()

def import_plugins():
    """
    Function to import plugins from the /plugins folder. Valid plugins are marked by <name>.is_sam_plugin == 1.
    """
    plugins = []
    #list files in /plugin folder
    filenames = glob.glob("plugins/*_plugin.py")
    core.log(name, "Importing Plugins: \n {filenames}".format(filenames = filenames))

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
    return "Running"

@app.route('/shutdown')
def shutdown():
    shutdown_server()
    return 'Server shutting down...'
'''
@app.route('/restart')
def restart():
    shutdown_server()
    main()
    return 'Server restarting...'
'''
def main():
    global threadID
    core.log(name, "Starting up!")
    t = flask_thread(threadID, "Flask")
    t.start()
    threads.append(t)
    threadID += 1
    #plugins = import_plugins()
    core.log(name, "Finished.")
    

if __name__ == "__main__":
    main()
    time.sleep(30)
    for t in threads:
        t.stop()
    

