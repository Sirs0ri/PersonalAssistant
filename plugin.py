#!/usr/bin/env python
# -*- coding: utf-8 -*-

class PluginBase:

    def set(object, target_state):
        #set object to target_state
        if True:
            return 1
        else: 
            return "Error. This shouldn't have happened!"

    def toggle(object):
        #toggle the state of object
        if True:
            return 1
        else: 
            return "Error. This shouldn't have happened!"  

    def run(self):
        print("running")
        
    def __init__(self):
        keywords = []
        has_toggle = 0
        has_set = 0
        self.run()