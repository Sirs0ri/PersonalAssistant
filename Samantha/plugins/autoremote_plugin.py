#!/usr/bin/env python
# -*- coding: utf-8 -*-

import core, time, imp, dropbox, requests, sys, traceback

is_sam_plugin = 1
name = "AutoRemote"
keywords = ["ar_message", "ar_file", "ar_notification", "onstart", "onexit"]
has_toggle = 0
has_set = 0

def send_file(device="g2", message="file", path=None):
    try:
        if path:
            destination = "/Samantha/file_{time}.png".format(time=time.strftime("%Y-%m-%d_%H:%M:%S", time.localtime()))
            #core.log(name, ["      Initializing the Dropbox-Client..."], "logging")
            client = dropbox.client.DropboxClient(core.private_variables.dropbox_token)
            f = open(path, 'rb')
            #core.log(name, ["      Uploading..."], "logging")
            response = client.put_file(destination, f)
            #core.log(name, ["      Accessing the public Link..."], "logging")
            response = client.share(destination, short_url=False)
            url = response["url"].replace("www.dropbox", "dl.dropboxusercontent").replace("?dl=0", "")
            #core.log(name, ["        {}".format(url)], "logging")
            payload = {'message': message, 'files': url}
            #core.log(name, ["      Sending the AR-Message..."], "logging")
            response = requests.get(core.private_variables.autoremote_baseurl["g2"], payload, timeout=20)
            return {"processed": True, "value": "The message {} with the file {} was sent successfully to {}".format(message, path, device), "plugin": name}
        else:
            return {"processed": False, "value": "Path not defined!", "plugin": name}
    except IOError as e:
        return {"processed": False, "value": "IOError: {}".format(e), "plugin": name}
    except KeyError as e:
        return {"processed": False, "value": "Device {} not found.".format(e), "plugin": name}
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
        #core.log(name, ["      Sending the AR-Message..."], "logging")
        response = requests.get(core.private_variables.autoremote_baseurl[device], payload, timeout=20)
        return {"processed": True, "value": "The message {} was sent successfully to {}".format(message, device), "plugin": name}
    except KeyError as e:
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
            result = send_file(device=params[0], message=params[1], path=params[2])
            return result
        elif key == "ar_message":
            result = send_file(device=params[0], message=params[1])
            return result
        else: 
            #core.log(name, ["  Illegal command.","  Key:{}".format(key),"  Parameters: {}".format(params)], "warning")
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
