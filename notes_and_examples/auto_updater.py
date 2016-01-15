#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
TO DO
* trigger: schedule plugin, hourly
* check if an update is available (via last downloaded commit)
* if yes:
    * copy current files to a backup location
    * pull the latest changes from GitHub
        * subprocess.Popen("home/pi/Desktop/update_git.sh")
    * stop and restart the server
    * wait 2 minutes for the "ok"
    * if there is no Ok-command: 
        * stop the server
        * restore the previously backed-up files
        * start the Server again
        * notify me
'''

