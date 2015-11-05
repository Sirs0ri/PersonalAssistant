#!/usr/bin/env python
# -*- coding: utf-8 -*-

# External module imports
import pigpio
import time

# Pin Definitons:
pi = pigpio.pi()
butPin = 17 # Broadcom pin 17 (P1 pin 11)



print("Here we go! Press CTRL+C to exit")
try:
    for i in range(20):
        pi.read(17)
        time.sleep(0.5)
except KeyboardInterrupt: # If CTRL+C is pressed, exit cleanly:
    exit()
