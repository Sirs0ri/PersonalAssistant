# PersonalAssistant

**I'm currently working on Samantha's 2nd iteration. The master-branch represents the stable version of the 1st one, the branch [sam_1.0](https://github.com/Sirs0ri/PersonalAssistant/tree/sam_1.0) is a backup of that and all the magic happens in [sam_2.0](https://github.com/Sirs0ri/PersonalAssistant/tree/sam_2.0).**

The home for Sam, Glyph, Will and all the other assistants out there

## What is what?

### Mainframe

    Samantha/main.py & Samantha/core.py

The "Mainframe" currently consists of main.py and core.py and is the framework in which Samantha operates.
Main.py is the file you want to run to start Samantha. It will start a very basic web-interface via **Flask** and handle starting the core. 
Core.py is a file that manages the different plugins. Upon being started by main.py, it imports and initializes the different plugins. It also provides the most important functions (process() and log(), to be exact) and handles system-wide variables.
Via the core's process() function communication between plugins becomes possible. It requires a keyword to work and takes parameters and a target as optional parameters.
When a command comes in, the core checks which Plugins can process it (via the keyword), forwards the data to them and then returns the results in a standardized format.

### Plugins

    Samantha/plugins/

Samantha's functionality comes from its different plugins. They can act as triggers/interface (see the Schedule-Plugin), pure processors (Identicon-Plugin) or a mix of both (433MHz-Transmitter-Plugin).
Every plugin has to fulfill a couple of requirements to be loaded successfully:
* It has to have a process()-function to handle input. 
* It has to declare it's name and which keywords it can handle, as well if it's meant to be loaded.

Plugins finally process the data received by interfaces. Each Plugin has a list of certain keywords. If a command matches any of these keywords, the plugin will be activated during the processing of the command by the mainframe.

Plugins can have different function such as:
- Interacting with other Soft-/Hardware (example: Home Automation)
- Communicate
- Researching (example: looking something up on Google, Wolfram Alpha, etc)
- Controlling (starting or manipulating the playback) Media

### Interfaces

The second part next to the Mainframe are Interfaces. They are used to receive data from the user, preprocess it into a standardized format, forward it to the mainframe and finally bring a result (might be for example a confirmation, refining question or an answer) back to the user.

The only interface for now is "Flask", a webserver which is started automatically via main.py and available in my local network.

Interfaces should have functions to:
- receive data from the user
- forward the preprocessed data to the mainframe
- log data from different modules
- display data directly to the user

## To Do

### Mainframe

#### Reorganize the framework

- [ ] plugins put data into an input-queue (core.trigger())
- [ ] a central processor reads the queue and processes the data (plugin.process())
- [ ] the processor puts data into an output-queue
- [ ] The interface reads the output-queue and displays the content
    - [ ] Update previous printouts when the progress changes -> only one line per processed command

#### Auto-updater

- [ ] trigger: schedule plugin, hourly
- [ ] check if an update is available (via last downloaded commit)
- [ ] if yes:
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

#### Processing
- [ ] react to input -> process()
- [ ] Multitasking
- [X] switch from process(key, param, comm) to process(key, params)

#### Other

- [ ] eyecandy: create a website that is shown on raspberrypi2:5000/ which allows to enter commands and restart/stop the server

### Plugins

#### light

- [ ] Transfer daemon to plugin 
- [ ] Dimming
    - [ ] Save the absolute values for Red, Green and Blue and the brightness to calculate the current value:
        - Red (R), Green (G) & Blue (B): min=0, max=255
        - Brightness (A): Decimal, min=0, max=1
        - the values for R, G and B are the brightest possible combination, A is the factor required to achieve the actual Color. Example "set(r=127, g=127, b=127)" becomes "set(r=255, g=255, b=255, a=0.5)"
    - [ ] Get brightest possible color while set()
    - [ ] apply brightness while crossFade(), when generating the spreaded List
- [ ] fix incompatibility with Flask and/or the RFSniffer
- Good RGB-value for warm white light?

#### Shows:

- [ ] find an episode from couchtuner's main page
- [ ] triggered by schedule_h = 5
- [ ] monitor my library to download only new episodes
- [ ] crossreference with Netflix and maybe Plex

#### Download

- [ ] trigger should contain a source location and a destination
- [ ] Download videos while I'm not sleeping: store a queue of links/filenames until then
- http://lifehacker.com/5475649/set-up-a-fully-automated-media-center

#### Presence

- [ ] Pings devices every couple of minutes and manages which ones are available
- [ ] Turn Light off, while I'm not at home
- [ ] Forward stored URLs as soon as a device becomes available
- [ ] Location based Reminders ("at Home")

#### Schedule

- [X] schedule Tasks, every 10 seconds/every minute/hour/day/month/year

#### 433

- [ ] fix incompatibility with the LED-Daemon
- [ ] increase performance of the receiver
- [X] send commands to devices using 433MHz signals
- [X] react to incoming 433MHz signals
- [ ] Cache current status of devices and send commands accordingly (Devices which will be toggled first, those that are already on/off last)
- http://www.princetronics.com/how-to-read-433-mhz-codes-w-raspberry-pi-433-mhz-receiver/

#### Chromecast

- [X] Dim Light while casting is active
- [ ] Remote Controls?
- https://github.com/balloob/pychromecast

#### Images

- [ ] speed improvements (currently takes roughly 90 sec from getting the command to finishing the upload)
    - [ ] combine iterating over the image multiple times into one action
    - [ ] Multithreading?
    - [ ] Create an image and store it for later use? (at 0.00: Send old image, then create a new "cached" one)
- [ ] finetuning of the shadow - maybe apply the blur to a 2x zoomed overlay and scale that down
- [X] grab an image from the earthview collection, add the colored overlay with shadows, eyecandy 'n stuff, and upload it to Dropbox; finally send it to my phone.
- [X] create a new wallpaper everyday at midnight and send it to the phone

#### A/V-Receiver

- [ ] turn on Receiver when my alarm goes off
- [ ] turn of receiver as soon as the night-profile is activated
- commands listed at https://drive.google.com/open?id=0B53k79HXVZRbZVhIdFIwb3Z1SEU
- send them via HTTP GET to <IP>/goform/formiPhoneAppDirect.xml?<COMMAND>

#### AutoRemote

- [ ] React to incoming messages
- [ ] React to URL-Messages
- [ ] Send messages
- [ ] Send files
- [ ] Send Notifications

#### Plex

- [ ] Integrate with the downloader
- [ ] suggest unseen episodes
- https://github.com/rueckstiess/py-plex
- https://github.com/mjs7231/python-plexapi

#### Mi Band

- [ ] Use it as Bluetooth Beacon
- [ ] read live sleep data
    - [ ] turn off music when the user falls asleep
    - [ ] run a "smart" alarm like the one integrated into the MiFit app, just with lights, music and everything
    - [ ] communicate with the user - eg. vibrate when a command is received/being processed/processed completely
- https://bitbucket.org/OscarAcena/mibanda

### Automation

- [ ] Save when which command is executed, find Patterns and then run Tasks automatically

### Other

- Eventghost 
    - magage autostart programs
        - while home
            - Input Director (only while PC is running as well) <-> Presence
