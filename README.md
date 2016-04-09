# PersonalAssistant

> This will be Samantha's second iteration.

> For the first version, see [here][sam_1.0].

> For the Repository contining Interfaces, see [here][interfaces].

## Idea

This is the second iteration of my Personal Assistant, Samantha. The program is supposed to run on a Raspberry Pi and manages both home automation, and "assisting duty" such as automatically creating a wallpaper every day, keeping track of the variant devices in my home network and notifying me about changes, etc.

Compared to it's first iteration, SAM2 will feature a more complex design.

The first version was split into the **core** and an interface for plugins. In addition to that, SAM2 will include a simple interface for **devices** and **services**. It'll also provide an easy exchangeable **user interface**. A completely new part will be the **context-module**. In combination with a set of rules, it should allow the program to learn and automate processes by itself. More information on that below.

![first_sketch]


## Services and devices

Samantha will provide interfaces for both, plugins/services and devices. These interfaces will take care of the communication with services/devices, instead of the core as it was the case in Samantha's first framework.

While the first version of the framework already supported talking to devices, this was so far only possible through a plugin. This version of Samantha will provide a unified interface for devices using the following standardized commands. Each device has to provide a .py file that implements these methods and thus allow Samantha to communicate with it independently from the services.

* required:
    * `turn_on()`
    * `turn_off()`
* optional:
    * `toggle()`
    * `set(property, new_value)`
    * `send_message(text)`


If possible, devices should report their availability to the context-module.

Services will continue using the current system using `process(keyword, data)`. The difference to Samantha 1.0 will be that the communication between services won't go through the core, but through an extra services-hub (which imports and starts them on startup).

## Context and rules

The context-module will store all kinds of information provided by the services and devices, such as the time (hh:mm, day/night time, etc), the location of a user, the commands of the last few minutes (I'm currently thinking about 5), which devices are available and whether they're on or not.

Whenever a command is processed, the current context is stored. The core will then analyze this database and search for patterns to create rules from. Rules will be created only if they are found with a high probability, that is at least 3 parameters have the same values in more than 95% of more than 10 cases (i.e. >=10/10, 19/20, 38/40, etc). Whenever the conditions of a rule are met (for example *time_of_day != day*, *chromecast_status = playing*, *chromecast_filetype != audio*) matching commands are triggered automatically (in this case the main light in the living room would turn off, and the ambient light would turn on).

## Core

The core will be the "*central processing unit*" of the whole framework. It'll receive input from the user via an input queue, process it and forward the commands to the devices-/services-modules. Also, as mentioned above it'll analyze the stored context repeatedly to find rules, and match the stored set of rules against the current context to execute commands automatically.

## Handler

There will be some kind of handler, starting all the main components and searching for updates n the background. If an update is found, it'll be downloaded to a temporary location, tested and if all goes as it should, the currently running version of that component is stopped, moved to a backup location and replaced by the newer version.

## User interface

User interfaces are a simple way for a user to pass commands to the core where they'll be processed. A UI can be a website, an app, or a service like AutoRemote or Slack, just to name a few. Different UIs will be developed in [a different repository][interfaces].

[first_sketch]: wiki/diagrams/first_sketch.png

[sam_1.0]: https://github.com/Sirs0ri/PersonalAssistant/tree/sam_1.0
[interfaces]: https://github.com/Sirs0ri/PersonalAssistant_Interfaces
