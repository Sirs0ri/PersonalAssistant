#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from flask import Flask,request
import core

"""
This is the main part, the "core" of Samantha.
It starts a Flask-Server which is used to receive commands (via Lan or localhost) on port 5000.

"""
name = "Mainframe"

app = Flask(__name__)

restart = 1

@app.route("/")
def process():
    """
    Process the data received via Flask
    Accesses the parameters "Keyword", "Parameter" and "Command"
    """
    #get parameters
    key = request.args.get('key')
    if not key:
        key = ""
    params = request.args.get('params')
    if not params:
        params = ""
    core.process(key=key, params=params.split("=:="), origin="Flask")
    return "Processing\nKeyword {}\nParameter {}".format(key,", ".join(params))

@app.route('/shutdown/')
def shutdown():
    """
    Shuts down first the Flask-Server, then every Thread started by the main module and all the plugins.
    """
    core.log("Incoming", ["Received the request to shut down."], "warning")
    func = request.environ.get("werkzeug.server.shutdown")
    if func is None:
        raise RuntimeError("Not running with the Werkzeug Server")
    func()
    core.log(name, ["  Flask stopped successfully. Waiting for plugins to stop."], "info")
    return 'Server shutting down...'

@app.route('/restart/')
def restart():
    """
    Restart the complete program. It'll shutdown Flask and set the Restart-Flag back to 1 so that main() will be executed again after it's completed (aka after Flask and the Plugins are shut down correctly.) 
    """
    global restart
    core.log(name, ["Received the request to restart."], "warning")
    restart = 1
    # this will cause main() to restart itself after the server's shut down.
    shutdown()
    return 'Server restarting...'

def main():
    """
    This is the main function. 
    It starts everything and does stuff.
    """
    global app
    global restart
    core.log(name, ["Starting up!","  ____    _    __  __    _    _   _ _____ _   _    _     "," / ___|  / \  |  \/  |  / \  | \ | |_   _| | | |  / \    "," \___ \ / _ \ | |\/| | / _ \ |  \| | | | | |_| | / _ \   ","  ___) / ___ \| |  | |/ ___ \| |\  | | | |  _  |/ ___ \  "," |____/_/   \_\_|  |_/_/   \_\_| \_| |_| |_| |_/_/   \_\ ","                                                     hi~"], "info")
    
    restart = 0
    startup = core.startup()
    '''
    if not startup:
        #initialisation went wrong, abort 
    '''
    core.log(name, ["Startup finished."], "logging")
        
    #don't log "INFO"-messages from Flask/werkzeug
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.WARNING)
    
    #app.debug = True
    core.log(name, ["Starting Flask."], "info")
    try:
        app.debug=True
        app.run(host="0.0.0.0")
    except Exception as e:
        core.log(name, ["{}".format(e)], "error")
    
    core.process(key="onexit", origin=name, target="all")
    core.log(name, ["  Plugins stopped."], "logging")
    
    #this'll be executed when Flask stops.
    core.log(name, ["Shut down successfully."], "info")

if __name__ == "__main__":
    while restart:
        main()
    core.log(name, ["See you next mission!","  ____    _    __  __    _    _   _ _____ _   _    _     "," / ___|  / \  |  \/  |  / \  | \ | |_   _| | | |  / \    "," \___ \ / _ \ | |\/| | / _ \ |  \| | | | | |_| | / _ \   ","  ___) / ___ \| |  | |/ ___ \| |\  | | | |  _  |/ ___ \  "," |____/_/   \_\_|  |_/_/   \_\_| \_| |_| |_| |_/_/   \_\ ","                                                    bye~"], "info")