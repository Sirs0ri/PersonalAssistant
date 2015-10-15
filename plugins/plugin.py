class Plugin_Base():
    
    def __init__(self):
        self.name = "Plugin"
        self.keywords = []
        self.has_toggle = 0
        self.has_set = 0

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