"""Samantha's server.web module."""


# standard library imports
import logging

# related third party imports
from flask import Flask, request

# application specific imports


__version__ = "1.0.0a2"

LOGGER = logging.getLogger(__name__)

app = Flask(__name__)


def start():
    LOGGER.info("Starting up!")
    app.run(host="127.0.0.1")
    
    
def stop():
    func = request.environ.get("werkzeug.server.shutdown")
    if func is None:
        raise RuntimeError("Not running with the Werkzeug Server")
    func()
    
    
@app.route("/callback/<id>")
def callback(id):
    data = request.args.get("data")
    LOGGER.info("Received data for callback on %s: %s", id, data)
    return ""


@app.route("/command/<comm>")
def command(comm):
    data = {}
    for key in request.args:
        data[key] = request.args[key]
    LOGGER.info("Received command %s, %s", comm, data)
    return ""
    
    
@app.route('/shutdown')
def shutdown_server():
    stop()
    return ""

LOGGER.info("I'm imported (server.web_server)")