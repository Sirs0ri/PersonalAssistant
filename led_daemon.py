#!/usr/bin/env python
 
import sys, os, time, atexit, pigpio
from signal import SIGTERM
 
pi = pigpio.pi()
 
redPins=[20,21]
greenPins=[25,12]
bluePins=[23,18]
 
class Daemon:
    """
   A generic daemon class.
   
   Usage: subclass the Daemon class and override the run() method
   """
    def __init__(self, pidfile, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.pidfile = pidfile
 
    def daemonize(self):
        """
       do the UNIX double-fork magic, see Stevens' "Advanced
       Programming in the UNIX Environment" for details (ISBN 0201563177)
       http://www.erlenstar.demon.co.uk/unix/faq_2.html#SEC16
       """
        try:
            pid = os.fork()
            if pid > 0:
                # exit first parent
                sys.exit(0)
        except OSError, e:
            sys.stderr.write("fork #1 failed: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(1)
   
        # decouple from parent environment
        os.chdir("/")
        os.setsid()
        os.umask(0)
   
        # do second fork
        try:
            pid = os.fork()
            if pid > 0:
                # exit from second parent
                sys.exit(0)
        except OSError, e:
            sys.stderr.write("fork #2 failed: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(1)
   
        # redirect standard file descriptors
        sys.stdout.flush()
        sys.stderr.flush()
        si = file(self.stdin, 'r')
        so = file(self.stdout, 'a+')
        se = file(self.stderr, 'a+', 0)
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())
   
        # write pidfile
        atexit.register(self.delpid)
        pid = str(os.getpid())
        file(self.pidfile,'w+').write("%s\n" % pid)
   
    def delpid(self):
        os.remove(self.pidfile)
 
    def start(self):
        """
       Start the daemon
       """
        # Check for a pidfile to see if the daemon already runs
        try:
            pf = file(self.pidfile,'r')
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
 
    def stop(self):
        """
        Stop the daemon
        """
        # Get the pid from the pidfile
        try:
            pf = file(self.pidfile,'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None
   
        if not pid:
            message = "pidfile %s does not exist. Daemon not running?\n"
            sys.stderr.write(message % self.pidfile)
            return # not an error in a restart
 
        # Try killing the daemon process       
        try:
            while 1:
                os.kill(pid, SIGTERM)
                time.sleep(0.1)
        except OSError, err:
            err = str(err)
            if err.find("No such process") > 0:
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)
            else:
                print str(err)
                sys.exit(1)
 
    def restart(self):
        """
        Restart the daemon
        """
        self.stop()
        self.start()
 
    def setPins(self, r=-1, g=-1, b=-1):
        if 0 <= r <= 255:
            for pin in redPins:
                pi.set_PWM_dutycycle(pin, r)
        if 0 <= g <= 255:
            for pin in greenPins:
                pi.set_PWM_dutycycle(pin, g)
        if 0 <= b <= 255:
            for pin in bluePins:
                pi.set_PWM_dutycycle(pin, b)
 
    def spread(self, m, n=256):
        if m < 0:
            m *= -1
        result = [0 for i in range (n)]
        if m < (n+1)//2:
            l = [i*n//m + n//(2*m) for i in range(m)]
        elif m > (n+1)//2:
            l = [x for x in range (n)]
            f = [i*n//(n-m) + n//(2*(n-m)) for i in range(n-m)]
            for item in f:
                l.remove(item)
        else:
            l = [i*2 for i in range(m)]
        for j in l:
            result[j] = 1
        return result
 
    def crossFade(self, r=-1, g=-1, b=-1, delay=0):
        if 0 <= r <= 255:
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
        self.crossFade(255,0,0,0.01)     	 #r=255,  g=0     b=0,    red
        while 1:
            self.crossFade(255,255,0,0.01)    #r=255,  g=255,  b=0,    yellow
            self.crossFade(0,255,0,0.01)      #r=0,    g=255,  b=0,    green
            self.crossFade(0,255,255,0.01)    #r=0,    g=255,  b=255,  cyan
            self.crossFade(0,0,255,0.01)      #r=0,    g=0,    b=255,  blue
            self.crossFade(255,0,255,0.01)    #r=255   g=0,    b=255,  magenta
            self.crossFade(255,0,0,0.01)      #r=255,  g=0,    b=0,    red
 
    def strobe(self):
        while 1:
            self.setPins(255,0,0)
            time.sleep(0.1)
            self.setPins(0,255,0)
            time.sleep(0.1)
            self.setPins(0,0,255)
            time.sleep(0.1)
 
    def toggle(self):
        if (abs(pi.get_PWM_dutycycle(20)) + abs(pi.get_PWM_dutycycle(25)) + abs(pi.get_PWM_dutycycle(23))):
            self.crossFade(0,0,0)
        else:
            self.crossFade(255,85,17)
        self.run()
        
    def set(self, r=-1, g=-1, b=-1, delay=0):
        self.crossFade(r, g, b, delay)
        self.run()
        
    def create(self):
        self.crossFade(255,0,0)  	 #r=255,  g=0     b=0,    red
        self.crossFade(255,255,0)    #r=255,  g=255,  b=0,    yellow
        self.crossFade(0,255,0)      #r=0,    g=255,  b=0,    green
        self.crossFade(0,255,255)    #r=0,    g=255,  b=255,  cyan
        self.crossFade(0,0,255)      #r=0,    g=0,    b=255,  blue
        self.crossFade(255,0,255)    #r=255   g=0,    b=255,  magenta
        self.crossFade(255,0,0)      #r=255,  g=0,    b=0,    red
        self.crossFade(0,0,0)
        self.run()
      
    def destroy(self):
        self.crossFade(0,0,0)
        self.stop()
        
    def run(self):
        while 1:
            time.sleep(1)
 
if __name__ == "__main__":
    daemon = Daemon(pidfile='/tmp/lightDaemon.pid')
    if len(sys.argv) >= 2:
        if 'start' == sys.argv[1]:
            print('Starting..')
            daemon.restart()
            daemon.create()
        elif 'stop' == sys.argv[1]:
            print('Stopping..')
            daemon.restart()
            daemon.destroy()
        elif 'Pause' == sys.argv[1]:
            print('Pausing..')
            daemon.restart()
        elif 'fade' == sys.argv[1]:
            print('Fading')
            daemon.restart()
            daemon.fade()
        elif 'strobe' == sys.argv[1]:
            print('Party Hard!')
            daemon.restart()
            daemon.strobe()
        elif 'toggle' == sys.argv[1]:
            print('Toggling')
            daemon.restart()
            daemon.toggle()
        elif 'set' == sys.argv[1]:
            try:
                redIn = int(sys.argv[2])
            except IndexError:
                redIn = 0
            try:
                greenIn = int(sys.argv[3])
            except IndexError:
                greenIn = 0
            try:
                blueIn = int(sys.argv[4])
            except IndexError:
                blueIn = 0
            if not (0 <= redIn <= 255):
                redIn = 0
            if not (0 <= greenIn <= 255):
                greenIn = 0
            if not (0 <= blueIn <= 255):
                blueIn = 0
            daemon.restart()
            daemon.set(r=redIn, g=greenIn, b=blueIn)
        else:
            print "Unknown command"
            sys.exit(2)
        sys.exit(0)
    else:
        print "usage: %s start|stop|restart" % sys.argv[0]
        sys.exit(2)