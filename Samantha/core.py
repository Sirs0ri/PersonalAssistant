#!/usr/bin/env python
# -*- coding: utf-8 -*-
import glob, imp, global_variables, urllib, sys, os, time, atexit
from signal import SIGTERM

name="Core"
plugins = []
key_index = {}

class str_format:
    """
    These formatters can be used to manipulate output via a console.
    Usage, for example for Bold, Red text:
    
        text = "TEXT"
        attr = ["1", "91"]
        s = "\033[{attrs}m{text}\33[0m".format(attrs = ";".join(attr), text=text)
        print s
    """
    ENDC = "0"
    BOLD = "1"
    UNDERLINE = "4"
    
    FG_BLACK = "30"
    FG_DARKGREY = "90"
    FG_LIGHTGREY = "37"
    FG_WHITE = "97"
    FG_DARKRED = "31"
    FG_LIGHTRED = "91"
    FG_DARKMAGENTA = "35"
    FG_LIGHTMAGENTA = "95"
    FG_DARKBLUE = "34"
    FG_LIGHTBLUE = "94"
    FG_DARKCYAN = "36"
    FG_LIGHTCYAN = "96"
    FG_DARKGREEN = "32"
    FG_LIGHTGREEN = "92"
    FG_DARKYELLOW = "33"
    FG_LIGHTYELLOW = "93"
    
    BG_BLACK = "40"
    BG_RED = "41"
    BG_GREEN = "42"
    BG_YELLOW = "43"
    BG_BLUE = "44"
    BG_MAGENTA = "45"
    BG_CYAN = "46"
    BG_WHITE = "47"

def log(name="None", content=["None"], level="logging"):
    """
    A simple logging-function that prints the input.
    
    TODO: Save log to a file, maybe upload it somewhere
    """
    if level == "error":
        lvl_str = "ERR "
        attr = [str_format.FG_LIGHTRED]
    elif level == "warning":
        lvl_str = "WARN" 
        attr = [str_format.FG_LIGHTYELLOW]
    elif level == "info":
        lvl_str = "INFO"
        attr = [str_format.FG_LIGHTCYAN]
    elif level == "logging":
        lvl_str = "INFO"
        attr = [str_format.FG_WHITE]
    elif level == "debug":
        lvl_str = "DEBG"
        attr = [str_format.FG_LIGHTMAGENTA]
    else:
        attr = []
        lvl_str="LVL"
        
    s = "[\033[{lvl_begin}m{lvl_str}{lvl_end}]\t{time}  {name}:\n\t  {content}".format(lvl_begin = ";".join(attr), lvl_str=lvl_str, lvl_end='\033[0m', time=time.strftime("%H:%M:%S", time.localtime()), name=name, content="\n\t  ".join(content))
    print(s)
    '''
    #log in file
    logfile=open("log.txt", 'r+')
    logfile.write(s)
    '''

def import_plugins():
    """
    Function to import plugins from the /plugins folder. Valid plugins are marked by <name>.is_sam_plugin == 1.
    """
    plugins = []
    plugin_names = []
    #list files in Samantha's /plugin folder
    log(name, ["Importing Plugins."], "info")
    filenames = glob.glob(global_variables.folder_base + "/plugins/*_plugin.py")
    log(name, ["  {} possible plugins found.".format(len(filenames))], "logging")

    #try importing each plugin
    for i in range(0,len(filenames)):
        log(name, ["  Found {}".format(filenames[i])], "logging")
        try:
            new_plugin = imp.load_source("samplugin{}".format(i), filenames[i])
            log(name, ["    Successfully imported {}.".format(filenames[i])], "logging")
            #Test if the imported file is a valid Plugin
            if new_plugin.is_sam_plugin:
                #add it to the list of plugins
                plugins.append(new_plugin)
                log(name, ["    Name: {}".format(new_plugin.name), "    Keywords: {}".format(new_plugin.keywords)], "logging")
                '''
                #initialize the plugin
                new_plugin.initialize()
                log(name, ["    {} initialized successfully".format(new_plugin.name, new_plugin.keywords)], "logging")
                '''
            else: 
                #is_sam_plugin == 0 -> the plugin is not supposed to be imported.
                log(name, ["    {} is not a valid Plugin (no error).".format(filenames[i])], "warning")
        except ImportError:
            log(name, ["  {} wasn't imported successfully.".format(filenames[i])], "error")
        except AttributeError:
            log(name, ["  {} is not a valid Plugin.".format(filenames[i])], "error")
    for p in plugins:
        plugin_names.append(p.name)
    log(name, ["Imported plugins:"] + plugin_names, "info")
    return plugins

def generate_index():
    """
    Generates and returns an index of keywords and the plugins that react to them.
    Exmple: key_index = {"344":[<433-Plugin>], "light":[<433-plugin>, <LED-Plugin>], "led":[<LED-Plugin>]}
    """
    global plugins
    key_index = {}
    log(name, ["Indexing Keywords"], "info")
    for p in plugins:
        for k in p.keywords:
            try:
                key_index[k].append(p)
            except KeyError:    #key isn't indexed yet
                key_index[k] = []
                key_index[k].append(p)
                log(name, ["  Created new Key: '{}'".format(k)], "logging")
    log(name, ["  Indexed Keywords."], "info")
    return key_index

def process(key, params=[], comm="None", origin="None"):
    """
    Process data
    Accesses the parameters "Keyword", "Parameter" and "Command"
    """
    log("Processing", ["New Command from {}:".format(origin),"Keyword {},".format(key),"Parameter {},".format(", ".join(params))], "info")
    global plugins
    results = {}
    try:
        for p in key_index[key]:
            log(name, ["  The plugin {} matches the keyword.".format(p.name)], "logging")
            results[p.name] = p.process(key, params)
    except KeyError as e:
        log(name, ["  This Keyword isn't indexed. [{}]".format(e)], "warning")
    return results

def startup():
    """
    This is the main function. 
    It starts everything and does stuff.
    """
    global plugins
    global key_index
    plugins = import_plugins()
    key_index = generate_index()
    for p in plugins:
        #initialize the plugin
        p.initialize()
        log(name, ["    {} initialized successfully".format(p.name, p.keywords)], "logging")
        
    log(name, ["Startup finished."], "info")
    return True

def shutdown():
    """
    Shuts down first the Flask-Server, then every Thread started by the main module and all the plugins.
    """
    global plugins
    log(name, ["Shutting down."], "info")
    log(name, ["  Waiting for plugins to stop."], "logging")
    for p in plugins:
        p.stop()
    log(name, ["  Plugins stopped."], "info")
    return True

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
