#!/usr/bin/env python
# -*- coding: utf-8 -*-
 
import sys, os, time, atexit, pigpio, threading
from signal import SIGTERM
import global_variables as gvars
import core


is_sam_plugin = 0
name = "LED"
keywords = ["led", "light"]
has_toggle = 1
has_set = 1

if is_sam_plugin:
    pi = pigpio.pi()

class LightDaemon(core.Daemon):
    """
    Deamon to control LED's using the "pigpio" Library (http://abyz.co.uk/rpi/pigpio/python.html)
    Offers functions to set a specific color, fade and strobe as well as a function to toggle the light.
    
    Credit for the Daemon to http://www.jejik.com/articles/2007/02/a_simple_unix_linux_daemon_in_python/
    """

    def start(self):
        """
        Start the daemon
        """
        # Check for a pidfile to see if the daemon already runs
        try:
            pf = file(self.pidfile,"r")
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None

        if pid:
            message = "pidfile %s already exist. Daemon already running?\n"
            sys.stderr.write(message % self.pidfile)
            sys.exit(1)

        # Start the daemon
        self.daemonize()
        #self.run()
        #self.run() must not be called here, because info is always transmitted via the call of another method. this won't work, if the daemon is already running
        
    def run(self):
        """
        Endless loop to keep the daemon alive after non-endless actions like setting the light to a specifiv color instead of for example fading indefinitely.
        This way, the daemon is always running and new states can be started via daemon.restart(); daemon.do_something_new()
        """
        while 1:
            time.sleep(1)
            
    def setPins(self, r=-1, g=-1, b=-1):
        """
        write values between 0 (=off) and 255 (=completely on) to the pins controlling the Lights
        
        gvars.<color>Pins is a list that holds the pinnumbers I'm currently using.
        """
        if 0 <= r <= 255:
            for pin in gvars.redPins:
                pi.set_PWM_dutycycle(pin, r)
        if 0 <= g <= 255:
            for pin in gvars.greenPins:
                pi.set_PWM_dutycycle(pin, g)
        if 0 <= b <= 255:
            for pin in gvars.bluePins:
                pi.set_PWM_dutycycle(pin, b)
 
    def spread(self, m, n=256):
        """
        Spread m "ones" ebenly in a list with the length n
        example: spread(3, 5) returns [1,0,1,0,1]
        """
        #first of all, catch negative values
        if m < 0:
            m *= -1

        #create an "empty" list filled with only zeroes
        result = [0 for i in range (n)]

        #Create a list with all the indices of items that will be set to 1. The code I'm using works perfectly while the number of entries to be spreaded over the whole list is less than half of the list's length. If that's not the case, the algorithm creates at first the inverse of the list and then inverts it. The 3rd case (m = n/2 for even n and m = (n+1)/2 for uneven n) simply creates a list with all even numbers between 0 and n.
        if m < (n+1)//2:
            l = [i*n//m + n//(2*m) for i in range(m)]
        elif m > (n+1)//2:
            l = [x for x in range (n)]
            f = [i*n//(n-m) + n//(2*(n-m)) for i in range(n-m)]
            for item in f:
                l.remove(item)
        else:
            l = [i*2 for i in range(m)]

        #Change every entry in the list to be returned of which the index is in the newly generated list to 1
        for j in l:
            result[j] = 1
        return result
 
    def crossFade(self, r=-1, g=-1, b=-1, delay=0):
        """
        crossfade from the current color to the given values in 255 steps.
        If a value is not between 0 and 255, it won't be changed
        
        the script can be slowed down via the variable "delay". It'll pause for the specified amount of seconds via time.sleep(delay) after setting each pin. 0 is used by default, 0.01 is used for example in fade(). 
        
        Be careful not to use too large values because the delay will be applied 255 times!
        """
        if 0 <= r <= 255:
            #calculate how many steps the single colors have to be turned up/down
            redIs = pi.get_PWM_dutycycle(20)
            redDiff = r - redIs
            redList = self.spread(m=redDiff)
        if 0 <= g <= 255:
            greenIs = pi.get_PWM_dutycycle(25)
            greenDiff = g - greenIs
            greenList = self.spread(m=greenDiff)
        if 0 <= b <= 255:
            blueIs = pi.get_PWM_dutycycle(23)
            blueDiff = b - blueIs
            blueList = self.spread(m=blueDiff)
            
        #then add/substract 1 for every 1 in the lists
        for i in range (256):
            if redList[i]:
                if redDiff < 0:
                    redIs -= 1
                elif redDiff > 0:
                    redIs += 1
                self.setPins(r=redIs)
                time.sleep(delay)
            if greenList[i]:
                if greenDiff < 0:
                    greenIs -= 1
                elif greenDiff > 0:
                    greenIs += 1
                self.setPins(g=greenIs)
                time.sleep(delay)
            if blueList[i]:
                if blueDiff < 0:
                    blueIs -= 1
                elif blueDiff > 0:
                    blueIs += 1
                self.setPins(b=blueIs)
                time.sleep(delay)
 
    def fade(self):
        """
        fades smoothly between different colors
        this is an endless loop which will be paused by stopping/restarting the daemon
        """
        self.crossFade(255,0,0,0.01)     	 #r=255,  g=0     b=0,    red
        while 1:
            self.crossFade(255,255,0,0.01)    #r=255,  g=255,  b=0,    yellow
            self.crossFade(0,255,0,0.01)      #r=0,    g=255,  b=0,    green
            self.crossFade(0,255,255,0.01)    #r=0,    g=255,  b=255,  cyan
            self.crossFade(0,0,255,0.01)      #r=0,    g=0,    b=255,  blue
            self.crossFade(255,0,255,0.01)    #r=255   g=0,    b=255,  magenta
            self.crossFade(255,0,0,0.01)      #r=255,  g=0,    b=0,    red
 
    def strobe(self):
        """
        flashes red, green and blue quickly
        this is an endless loop which will be paused by stopping/restarting the daemon
        """
        while 1:
            self.setPins(255,0,0)
            time.sleep(0.1)
            self.setPins(0,255,0)
            time.sleep(0.1)
            self.setPins(0,0,255)
            time.sleep(0.1)
 
    def toggle(self):
        """
        turns on a warm-white light if the LEDs are completely off and turns them off otherwise
        """
        #get the values of the pins for each color, if all 3 are 0 the light is completely off, otherwise it will be turned off.
        if (abs(pi.get_PWM_dutycycle(20)) + abs(pi.get_PWM_dutycycle(25)) + abs(pi.get_PWM_dutycycle(23))):
            self.crossFade(0,0,0)
        else:
            self.crossFade(255,85,17)

        #keep the daemon alive. For a more detailed explanation, see the comments to the run()-method itself!
        self.run()

    def set(self, r=-1, g=-1, b=-1, delay=0):
        """
        crossfades to a given color and then keeps the daemon alive
        if a color is not specified (or -1) it won't be changed
        """

        self.crossFade(r, g, b, delay)

        #keep the daemon alive. For a more detailed explanation, see the comments to the run()-method itself!
        self.run()
    '''
    def dim(self, brightness=1.0, delay=0):
        """
        change the brightness of the light. possible inputs are -x and +x to add/substract values and x to set a new brightness independendly of the current one.
        """
        #get current values
        r = pi.get_PWM_dutycycle(20)
        g = pi.get_PWM_dutycycle(25)
        b= pi.get_PWM_dutycycle(23)

        if "-" in str(brightness) or "+" in str(brightness):
            #get current brightness
            limit=max(r, g, b)
            #set new threshold, negative values will be substracted, positive ones will be added
            brightness = (limit/255) + brightness
            if brightness < 0.0:
                brightness = 0.0
            elif brightness > 1.0:
                brightness = 1.0

        if 0.0 <= brightness <= 1.0:
            current_max = max(r, g, b)
            if current_max:
                factor = (max(r, g, b)/255) * brightness
            else:
                factor = brightness
            r *= factor
            g *= factor
            b *= factor
            self.crossFade(r, g, b, delay)

        self.run()
    '''
    def create(self):
        """
        crossfades over the major colors, then turns off again; Mostly for debugging
        """
        self.start()
        self.crossFade(255,0,0)  	 #r=255,  g=0     b=0,    red
        self.crossFade(255,255,0)    #r=255,  g=255,  b=0,    yellow
        self.crossFade(0,255,0)      #r=0,    g=255,  b=0,    green
        self.crossFade(0,255,255)    #r=0,    g=255,  b=255,  cyan
        self.crossFade(0,0,255)      #r=0,    g=0,    b=255,  blue
        self.crossFade(255,0,255)    #r=255   g=0,    b=255,  magenta
        self.crossFade(255,0,0)      #r=255,  g=0,    b=0,    red
        self.crossFade(0,0,0)

        #keep the daemon alive. For a more detailed explanation, see the comments to the run()-method itself!
        self.run()

    def destroy(self):
        """
        turns the light off and stops the daemon
        """
        self.crossFade(0,0,0)
        self.stop()

class Plugin_Thread(threading.Thread):
    
    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = name + "_Thread"
        self.daemon = LightDaemon(pidfile="/tmp/lightDaemon.pid")
        
    def run(self):
        core.log(self.name, "Starting")
        core.log(self.name, "Initializing 1")
        self.daemon.create()
        core.log(self.name, "Initialized")
        
    def stop(self):
        core.log(self.name, "  Exiting")
        self.daemon.restart()
        self.daemon.destroy()
        
t = Plugin_Thread(name)

def initialize():
    global t
    t.start()

def stop():
    global t
    t.stop()

def process(key, param, comm):
    global t
    if key == "led":
        if param == "pause":
            print("Pausing..")
            t.daemon.restart()
            core.log(name, "  LEDs Paused.")
        elif param == "fade":
            t.daemon.restart()
            t.daemon.fade()
            core.log(name, "  LEDs now fading.")
        elif param == "strobe":
            t.daemon.restart()
            t.daemon.strobe()
            core.log(name, "  Party mode activated.")
        elif param == "toggle":
            t.daemon.restart()
            t.daemon.toggle()
            core.log(name, "  Toggled the light.")
        elif param == "set":
            #check that the values the light will be set to are valid as numbers between 0 and 255.
            try:
                redIn = int(comm[0])
            except IndexError:
                redIn = 0
            try:
                greenIn = int(comm[1])
            except IndexError:
                greenIn = 0
            try:
                blueIn = int(comm[2])
            except IndexError:
                blueIn = 0
            if not (0 <= redIn <= 255):
                redIn = 0
            if not (0 <= greenIn <= 255):
                greenIn = 0
            if not (0 <= blueIn <= 255):
                blueIn = 0
            t.daemon.restart()
            t.daemon.set(r=redIn, g=greenIn, b=blueIn)
            core.log(name, "  Set the LEDs to ({},{},{}).".format(redIn, greenIn, blueIn))
        '''
        elif "dim" == sys.argv[1]:
            print("Changing Brightness")
            try:
                brightness = float(sys.argv[2])
            except IndexError:
                brightness = 1.0
            print("Changing Brightness to %f" % brightness)
            daemon.restart()
            daemon.dim(brightness)
        '''
    elif key == "light":
        if param == "off":
            t.daemon.restart()
            t.daemon.set(r=0, g=0, b=0)
            core.log(name, "Set the LEDs to (0,0,0).")
        elif param == "on":
            t.daemon.restart()
            t.daemon.set(r=255, g=85, b=17)
            core.log(name, "Set the LEDs to (255,85,17).")