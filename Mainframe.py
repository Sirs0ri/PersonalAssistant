#!/usr/bin/env python

def import_plugins():
    #get filenames of python files in /plugins
    plugins = []
    for f in filenames:
        import f
        if f.is_sam_plugin:
            plugins.append(f.Plugin())

def start_interfaces():
    interfaces = []
    #read config
    #import Interfaces according to config
    for i in interfaces:
        i.start()

def log(content):
    for i in interfaces:
        i.log(content)

def output(content):
    for i in interfaces:
        i.output(content)

def set_config(key, value):
    #read config file
    for l in config_file:
        if key in l:
            #replace with key:value

if __name__ == "__main__":
    import_plugins()
    start_interfaces()
    log("Plugins imported")
    log("Interfaces started")
    
    
'''
def set_something(plugin_keyword, object, target_state):
    for p in plugins:
        if keyword in p.keywords and p.has_set:
            result = p.set(object, target_state)
            if result == 1
                pass
            else
                print("Error from {name}: {description}".format(name=p.name, description=result))

def get_something(plugin_keyword, object, target_state):
    for p in plugins:
        if keyword in p.keywords and p.has_set:
            result = p.set(object, target_state)
            if result == -1
                print("Error from {name}: {description}".format(name=p.name, description=result))
            else
                #process Result, could be path to a file, link, etc
                pass

def toggle_something(plugin_keyword, object):
    for p in plugins:
        if keyword in p.keywords and p.has_toggle:
            result = p.toggle(object)
            if result == 1
                pass
            else
                print("Error from {name}: {description}".format(name=p.name, description=result))
'''