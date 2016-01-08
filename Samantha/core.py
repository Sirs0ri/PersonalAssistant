#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib, sys, os, time, atexit
from signal import SIGTERM

def generate_index():
    """
    Generates and returns an index of keywords and the plugins that react to them.
    Exmple: key_index = {"344":[<433-Plugin>], "light":[<433-plugin>, <LED-Plugin>], "led":[<LED-Plugin>]}
    """
    global plugins
    key_index = {}
    log(name, ["Indexing Keywords"])
    for p in plugins:
        for k in p.keywords:
            try:
                key_index[k].append(p)
            except KeyError:    #key isn't indexed yet
                key_index[k] = []
                key_index[k].append(p)
                log(name, ["  Created new Key: '{}'".format(k)])
    log(name, ["  Indexed Keywords."])
    return key_index

def process(key, param="None", comm="None"):
    """
    Process the data received via Flask
    Accesses the parameters "Keyword", "Parameter" and "Command"
    """
    global plugins
    log(name, ["Processing:","Keyword {},".format(key),"Parameter {},".format(param),"Command {}".format(comm)])
    #process the command
    processed = 0
    '''
    try:
        for p in key_index[key]:
            log(name, ["  The plugin {} matches the keyword.".format(p.name)])
            p.process(key, param, comm)
            processed=1
    except KeyError as e:
        log(name, ["  Error: This Keyword isn't indexed. [{}]".format(e)])
    '''
    for p in key_index[key]:
        log(name, ["  The plugin {} matches the keyword.".format(p.name)])
        p.process(key, param, comm)
        processed=1
    if not processed:
        log(name, ["  No matching Plugin found."])
    return "Processing\nKeyword {}\nParameter {}\nCommand {}".format(key,param,comm)

class Daemon:
    """
    A generic daemon class.
    
    Usage: subclass the Daemon class and override the run() method
    """
    def __init__(self, pidfile, stdin="/dev/null", stdout="/dev/null", stderr="/dev/null"):
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
        si = file(self.stdin, "r")
        so = file(self.stdout, "a+")
        se = file(self.stderr, "a+", 0)
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())
    
        # write pidfile
        atexit.register(self.delpid)
        pid = str(os.getpid())
        file(self.pidfile,"w+").write("%s\n" % pid)
    
    def delpid(self):
        os.remove(self.pidfile)

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
        self.run()

    def stop(self):
        """
        Stop the daemon
        """
        # Get the pid from the pidfile
        try:
            pf = file(self.pidfile,"r")
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

    def run(self):
        """
        You should override this method when you subclass Daemon. It will be called after the process has been
        daemonized by start() or restart().
        """

name="Core"
#def log(interfaces, name="", content=""):
def log(name="None", content=["None"], level="info"):
    
    #print to the script calling .log(); usually Mainframe.py
    l = len(name)
    if l < 9:
        name += " " * (9-l)
    s = "{name}\t{time}: {content}".format(name=name, time=time.strftime("%H:%M:%S", time.localtime()), content="\n                            ".join(content))
    print(s)
    '''
    #log in file
    logfile=open("log.txt", 'r+')
    logfile.write(s)
    '''

def get_answer(k, p=None, c=None, attempt=1):
    key = urllib.urlencode({"key":k})
    param = urllib.urlencode({"param":p})
    comm = urllib.urlencode({"comm":c})
    if attempt < 5:
        try:
            answer = urllib.urlopen("http://127.0.0.1:5000/?{k}&{p}&{c}".format(k=key, p=param, c=comm)).read()
        except IOError:
            log(name, ["Couldn't connect to Flask. Retrying in 5 seconds."])
            time.sleep(5)
            attempt += 1
            answer = get_answer(k, p, c, attempt)
    else:
        log(name, ["aborted command {}, {}, {}".format(k, p, c)])
        answer = "!CONNECTION_ERROR"
    if answer:
        return answer
    else:
        return "!NULL_ANSWER"