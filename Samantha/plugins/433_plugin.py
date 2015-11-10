#!/usr/bin/env python
# -*- coding: utf-8 -*-

import core, subprocess, os

is_sam_plugin = 1
name = "433MHz"
keywords = []
has_toggle = 0
has_set = 0

process = None

def run_command():
    global process
    process = subprocess.Popen("sudo /home/pi/Desktop/libraries/433Utils/RPi_utils/RFSniffer", stdout=subprocess.PIPE)
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            core.log(name, output.strip())
    rc = process.poll()
    return rc

def initialize():
    global process
    core.log(name, "Starting thread.")
    process = subprocess.Popen("sudo /home/pi/Desktop/libraries/433Utils/RPi_utils/RFSniffer", stdout=subprocess.PIPE)
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            core.log(name, output.strip())
    core.log(name, "Not running anymore.")

def stop():
    global process
    core.log(name, "Exiting")
    os.kill(process.pid, signal.SIGTERM)
