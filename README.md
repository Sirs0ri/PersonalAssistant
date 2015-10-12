# PersonalAssistant
The home for Sam, Glyph, Will and all the other assistants out there

## To Do

* Plugins
    - "mainframe" that reads a folder and imports .py files
    - usage: mainframe.py <operation[set, get, toggle, etc]> <plugin_keyword> <data>

    ```python
    def import_plugins():
        for f in filenames:
            import f
            if f.is_sam_plugin:
                plugins.append(f.Plugin())
    
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
            
    ```
    
    - Plugins

    ```python
    is_sam_plugin = 1
    plugin_name = "Plugin_Example"
    
    class Plugin():
        
        def __init__(self, input):
            self.name = "Plugin_Example"
            self.keywords = ["eat", "sleep", "rave", "repeat"]
            self.has_toggle = 1
            self.has_set = 1
    
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
    ```


* light
    - Save {"red":<redValue[0-255]>, "green":<greenValue[0-255]>, "blue":<blueValue[0-255]>, "brightness":<redValue[Decimal(0-1)]>}
    - dim(): use Decimal() as factor 
    - store original color, always start dimming with that color
    - Get brightest possible color while set()
    - apply brightness while crossFade(), when generating the spreaded List

* Network
    - Framework in which our different PA'a communicate?

* Download
    - Check every X minutes for new episodes
    - Will's code to download Videos?

* Ping/Presence
    - Pings devices every couple of minutes and manages which ones are available
    - example: Force light to be off, if phone is not at home

* Eventghost 
    - magage autostart programs
        - while home
            - Input Director (only while PC is running as well)
