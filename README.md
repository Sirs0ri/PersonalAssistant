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

### Mainframe

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

#### Download

- [ ] trigger should contain a source location and a destination
- [ ] Download videos while I'm not sleeping: store a queue of links/filenames until then

#### Presence

- [ ] Pings devices every couple of minutes and manages which ones are available
- [ ] Turn Light off, while I'm not at home
- [ ] Forward stored URLs as soon as a device becomes available
- [ ] Location based Reminders ("at Home")

#### Schedule

- [ ] schedule Tasks, every x*5 minutes/hourly
    - [X] hourly
    - [X] every x*5 minutes since start
    - [ ] every x minutes (0:00, 0:05, 0:10, etc)

#### 433

- [ ] fix incompatibility with the LED-Daemon
- [ ] increase performance of the receiver
- [X] send commands to devices using 433MHz signals
- [X] react to incoming 433MHz signals
- [ ] Cache current status of devices and send commands accordingly (Devices which will be toggled first, those that are already on/off last)
- http://www.princetronics.com/how-to-read-433-mhz-codes-w-raspberry-pi-433-mhz-receiver/

#### Chromecast

- [ ] Dim Light while casting is active
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

### Automation

- [ ] Save when which command is executed, find Patterns and then run Tasks automatically

### Other

- Eventghost 
    - magage autostart programs
        - while home
            - Input Director (only while PC is running as well) <-> Presence
