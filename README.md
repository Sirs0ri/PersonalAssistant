# PersonalAssistant
The home for Sam, Glyph, Will and all the other assistants out there

## To Do

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
            - Dell Display Manager (detect when the monitor is plugged in?)
            - Music/Photos Upload
            - Plex
            - Input Director (only while PC is running as well)
        - When Device connected?
            - Mouse- and Keyboarddriver