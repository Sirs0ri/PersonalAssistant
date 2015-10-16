# PersonalAssistant
The home for Sam, Glyph, Will and all the other assistants out there

## To Do

- "Mainframe" that reads a folder and imports .py files
    - start interfaces
    - react to input

- Interfaces
    - bring input back to the Mainframe
        - > Interrupt?
        - > Call to 127.0.0.1:XYZ?
    - CMD
    - GUI?
    - Will, Glyph?
    
- Plugins
    - light
        - Transfer daemon to plugin 
        - Save {"red":redValue[0-255], "green":greenValue[0-255], "blue":blueValue[0-255], "brightness":redValue[Decimal(0-1)]}
        - dim(): use Decimal() as factor 
        - store original color, always start dimming with that color
        - Get brightest possible color while set()
        - apply brightness while crossFade(), when generating the spreaded List
    - Download
        - Check every X minutes for new episodes
        - Will's code to download Videos?
    - Presence
        - Pings devices every couple of minutes and manages which ones are available
        - example: Force light to be off, if phone is not at home

* Eventghost 
    - magage autostart programs
        - while home
            - Input Director (only while PC is running as well) <-> Presence
