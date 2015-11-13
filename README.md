# PersonalAssistant
The home for Sam, Glyph, Will and all the other assistants out there

## What is what?

### Mainframe

The "Mainframe" is the framework in which Samantha operates.
It manages plugins and interfaces and the communication between the independent components. Some important functions which can be called by both, the mainframe and imported plugins are handled by a separate core which can be imported by the Mainframe and both, plugins and interfaces. An example is the "log()" function which is used to transfer data from every part of Sam to the active interfaces.

The mainframe's function is to receive data from an Interface, distribute it to the correct plugin(s), collect the answers and direct the answers back to the Interface it came from as "output" and to ecery other interface as part of the log.

### Interfaces

The second biggest part next to the Mainframe are Interfaces. They are used to receive data from the user, preprocess it into a standardized format, forward it to the mainframe and finally bring a result (might be for example a confirmation, refining question or an answer) back to the user.

Interfaces should have functions to:
- receive data from the user
- forward the preprocessed data to the mainframe
- log data from different modules
- display data directly to the user

### Plugins

Plugins finally process the data received by interfaces. Each Plugin has a list of certain keywords. If a command matches any of these keywords, the plugin will be activated during the processing of the command by the mainframe.

Plugins can have different function such as:
- Interacting with other Soft-/Hardware (example: Home Automation)
- Communicate
- Researching (example: looking something up on Google, Wolfram Alpha, etc)
- Controlling (starting or manipulating the playback) Media

## To Do

- "Mainframe" that reads a folder and imports .py files
    - Auto-updater
        - trigger: schedule plugin, hourly
        - check if an update is available (via last downloaded commit)
        - if yes:
            - copy current files to a backup location
            - pull the latest changes from GitHub
                - subprocess.Popen("home/pi/Desktop/update_git.sh")
            - stop and restart the server
            - wait 2 minutes for the "ok"
            - if there is no Ok-command: 
                - stop the server
                - restore the previously backed-up files
                - start the Server again
            - notify me about success/failure
    - react to input -> process()
    - eyecandy: create a website that is shown on raspberrypi2:5000/ which allows to enter commands and restart/stop the server

- Plugins
    - light
        - Transfer daemon to plugin 
        - Save {"red":redValue[0-255], "green":greenValue[0-255], "blue":blueValue[0-255], "brightness":redValue[Decimal(0-1)]}
        - dim(): use Decimal() as factor while crossFade()
        - store original color, always start dimming with that color
        - Get brightest possible color while set()
        - apply brightness while crossFade(), when generating the spreaded List
    - Shows:
        - find an episode from couchtuner's main page
        - triggered by schedule_h = 5
    - Download
        - trigger should contain a source location and a destination
        - Download videos while I'm not sleeping: store a queue of links/filenames until then
    - Presence
        - Pings devices every couple of minutes and manages which ones are available
        - example: Force light to be off, if phone is not at home
    - 433
        - http://www.princetronics.com/how-to-read-433-mhz-codes-w-raspberry-pi-433-mhz-receiver/
        - Done: send commands to devices using 433MHz signals
        - Done: react to incoming 433MHz signals
    - Chromecast
        - https://github.com/balloob/pychromecast
        - Remote Controls?
        - Dim Light while casting is active

* Eventghost 
    - magage autostart programs
        - while home
            - Input Director (only while PC is running as well) <-> Presence
