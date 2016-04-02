#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import sys
import traceback

import core
from flask import Flask, request

"""
This is the main part, the "core" of Samantha.
It starts a Flask-Server which is used to receive commands (via LAN or localhost)
on port 5000 and initializes the plugins via 'core'.
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
    # get parameters
    key = request.args.get('key')
    if not key:
        key = ""
    params = request.args.get('params')
    if not params:
        params = ""
    core.process(key=key, params=params.split("=:="), origin="Flask", target="all", type="trigger")
    return "Processing\nKeyword {}\nParameter {}".format(key, ", ".join(params))


@app.route('/shutdown/')
def shutdown_server():
    """
    Shuts down first the Flask-Server,
    then every Thread started by the main module and all the plugins.
    """
    core.log("Incoming", ["Received the request to shut down."], "warning")
    func = request.environ.get("werkzeug.server.shutdown")
    if func is None:
        raise RuntimeError("Not running with the Werkzeug Server")
    func()
    core.log(name, ["  Flask stopped successfully. Waiting for plugins to stop."], "info")
    return 'Server shutting down...'


@app.route('/restart/')
def restart_server():
    """
    Restart the complete program. It'll shutdown Flask and set the Restart-Flag back to 1
    so that main() will be executed again after it's completed
    (aka after Flask and the Plugins are shut down correctly.)
    """
    global restart
    core.log(name, ["Received the request to restart."], "warning")
    restart = 1
    # this will cause main() to restart itself after the server's shut down.
    shutdown_server()
    return 'Server restarting...'


def main():
    """
    This is the main function.
    It starts everything and does stuff.
    """
    global app
    global restart
    core.log(name, ["",
                    " ____    _    __  __    _    _   _ _____ _   _    _     ",
                    "/ ___|  / \  |  \/  |  / \  | \ | |_   _| | | |  / \    ",
                    "\___ \ / _ \ | |\/| | / _ \ |  \| | | | | |_| | / _ \   ",
                    " ___) / ___ \| |  | |/ ___ \| |\  | | | |  _  |/ ___ \  ",
                    "|____/_/   \_\_|  |_/_/   \_\_| \_| |_| |_| |_/_/   \_\ ",
                    "                                                    hi~ ",
                    "Starting up!"], "info")

    restart = 0
    startup = core.startup()

    if not startup:
        print "Startup not successful!"

    # don't log "INFO"-messages from Flask/werkzeug
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.WARNING)

    # app.debug = True
    core.log(name, ["Starting Flask..."], "info")
    try:
        app.run(host="0.0.0.0")
    except Exception as e:
        print "-"*60
        print "Exception in user code:"
        print "-"*60
        traceback.print_exc(file=sys.stdout)
        print "-"*60
        core.log(name, ["{}".format(e)], "error")

    core.process(key="onexit", origin=name, target="all")
    core.log(name, ["  Plugins stopped."], "logging")

    # this'll be executed when Flask stops.
    core.log(name, ["Shut down successfully."], "info")

if __name__ == "__main__":
    while restart:
        main()
    core.log(name, ["See you next mission!",
                    " ____    _    __  __    _    _   _ _____ _   _    _     ",
                    "/ ___|  / \  |  \/  |  / \  | \ | |_   _| | | |  / \    ",
                    "\___ \ / _ \ | |\/| | / _ \ |  \| | | | | |_| | / _ \   ",
                    " ___) / ___ \| |  | |/ ___ \| |\  | | | |  _  |/ ___ \  ",
                    "|____/_/   \_\_|  |_/_/   \_\_| \_| |_| |_| |_/_/   \_\ ",
                    "                                                   bye~ "], "info")
