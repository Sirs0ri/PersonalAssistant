#!/usr/bin/env python
# -*- coding: utf-8 -*-

import core, time, imp, dropbox, requests, sys, traceback

"""
This plugin's purpose is sending messages via AutoRemote (developed by Joao Dias, http://joaoapps.com/autoremote/) to other devices.
The plugin currently supports only sending mesages and files to phones, sending notifications in general and messages to PCs is planned for the future, as well as receiving messages.
"""

is_sam_plugin = 1
name = "AutoRemote"
keywords = ["ar_message", "ar_file", "ar_notification", "onstart", "onexit"]
has_toggle = 0
has_set = 0

def send_file(device="g2", message="file", path=None, destination=None):
    """
    This method sends a file to a given device. Therefore, the file must be uploaded somewhere AutoRemote can access it. I'm using Dropbox for now, an implementation of Google Drive is planned (AutoRemote uses their API and has access to my drive from the Android App. This would allow me to upload the files not publicly for everyone).
    """
    try:
        if path:
            # Set the destination, where in my Dropbox the file should be saved.
            if not destination:
                destination = "/Samantha/file_{time}.{ending}".format(time=time.strftime("%Y-%m-%d_%H:%M:%S", time.localtime()), ending=path.split(".")[-1])
            # Initialize the Dropbox-client
            client = dropbox.client.DropboxClient(core.private_variables.dropbox_token)
            f = open(path, 'rb')
            # Upload the file to Dropbox
            response = client.put_file(destination, f)
            # Access the files public link
            response = client.share(destination, short_url=False)
            # The link leads to a site where the file is displayed. To accedd the direct link to the file, only a part of the URL has to be replaced.
            url = response["url"].replace("www.dropbox", "dl.dropboxusercontent").replace("?dl=0", "")
            # Finally, send the actual message via 'requests'
            payload = {'message': message, 'files': url}
            response = requests.get(core.private_variables.autoremote_baseurl["g2"], payload, timeout=20)
            return {"processed": True, "value": "The message {} with the file {} was sent successfully to {}".format(message, path, device), "plugin": name}
        else:
            return {"processed": False, "value": "Path not defined!", "plugin": name}
    except IOError as e:
        # Something probably went wrong with the file.
        return {"processed": False, "value": "IOError: {}".format(e), "plugin": name}
    except KeyError as e:
        # This means that the dict 'core.private_variables.autoremote_baseurl' doesn't include the baseurl of the requested device.
        return {"processed": False, "value": "Device {} not found.".format(e), "plugin": name}
    except requests.exceptions.Timeout as e:
        return {"processed": False, "value": "Timeout while sending the message. ({})".format(e), "plugin": name}
    except Exception as e:
        print("-"*60)
        print("Exception in user code:")
        print("-"*60)
        traceback.print_exc(file=sys.stdout)
        print("-"*60)
        return {"processed": False, "value": "Unhandled Exception: {}".format(e), "plugin": name}

def send_message(device="g2", message="file"):
    try:
        payload = {'message': message}
        # This just sends a message via the 'requests' library.
        response = requests.get(core.private_variables.autoremote_baseurl[device], payload, timeout=20)
        return {"processed": True, "value": "The message {} was sent successfully to {}".format(message, device), "plugin": name}
    except KeyError as e:
        # This means that the dict 'core.private_variables.autoremote_baseurl' doesn't include the baseurl of the requested device.
        return {"processed": False, "value": "Device {} not found.".format(e), "plugin": name}
    except requests.exceptions.Timeout as e:
        return {"processed": False, "value": "Timeout while sending the message. ({})".format(e), "plugin": name}
    except Exception as e:
        print("-"*60)
        print("Exception in user code:")
        print("-"*60)
        traceback.print_exc(file=sys.stdout)
        print("-"*60)
        return {"processed": False, "value": "Unhandled Exception: {}".format(e), "plugin": name}

def process(key, params):
    try:
        if key == "onstart":
            result = send_message(message="sam_onstart")
            return result
        elif key == "onexit":
            result = send_message(message="sam_onexit")
            return result
        elif key == "ar_file":
            if "wallpaper.set" in params:
                result = send_file(device=params[0], message=params[1], path=params[2], destination="/Wallpapers/wallpaper_{time}.png".format(time=time.strftime("%Y-%m-%d_%H:%M:%S", time.localtime())))
            else:
                result = send_file(device=params[0], message=params[1], path=params[2])
            return result
        elif key == "ar_message":
            result = send_file(device=params[0], message=params[1])
            return result
        else: 
            return {"processed": False, "value": "Keyword not in use. ({}, {})".format(key, params), "plugin": name}
    except KeyError as e:
        return {"processed": False, "value": "Missing Parameter ({})".format(e), "plugin": name}
    except Exception as e:
        print("-"*60)
        print("Exception in user code:")
        print("-"*60)
        traceback.print_exc(file=sys.stdout)
        print("-"*60)
        core.log(name, ["{}".format(e)], "error")
        return {"processed": False, "value": e, "plugin": name}
