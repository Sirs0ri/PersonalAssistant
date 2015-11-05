#!/usr/bin/env python
# -*- coding: utf-8 -*-

# External module imports
import RPi.GPIO as GPIO

# Pin Definitons:

butPin = 17 # Broadcom pin 17 (P1 pin 11)


# Pin Setup:
GPIO.setmode(GPIO.BCM) # Broadcom pin-numbering scheme
GPIO.setup(butPin, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Button pin set as input w/ pull-up

print("Here we go! Press CTRL+C to exit")
try:
    while 1:
        if GPIO.input(butPin): # button is released
            print("in 1")
            print(GPIO.input(butPin))
        else: # button is pressed:
            print("in 2")
except KeyboardInterrupt: # If CTRL+C is pressed, exit cleanly:
    exit()
