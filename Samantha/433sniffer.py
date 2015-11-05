#!/usr/bin/env python
# -*- coding: utf-8 -*-

# External module imports
import pigpio
import time

# Pin Definitons:
pi = pigpio.pi()



print("Here we go! Press CTRL+C to exit")
try:
    while 1:
        if pi.read(17): # button is released
            print("in 1")
            print(pi.read(17))
            time.sleep(0.5)
        else: # button is pressed:
            print("in 2")
            print(pi.read(17))
            time.sleep(0.5)
except KeyboardInterrupt: # If CTRL+C is pressed, exit cleanly:
    exit()