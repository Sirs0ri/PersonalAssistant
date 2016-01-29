#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re, pydenticon, core, time, requests, dropbox, imp, sys, traceback
from PIL import Image, ImageChops, ImageEnhance, ImageFilter, ImageOps

"""
This plugin is supposed to handle everything image-related.
Currently, it is used to create a wallpaper from an image out of Google's 'EarthView' collection. 
Examples can be seen at https://www.dropbox.com/sh/gz0aj2ghcf1p02s/AADp8WdhRRcMaHusyvjY2IOfa?dl=0
"""

is_sam_plugin = 1
name = "Images"
keywords = ["schedule_day", "wallpaper", "set_wallpaper"]
has_toggle = 0
has_set = 0

DEBUG = 0

def get_wallpaper():
    """
    This method downloads an image from Google's EarthView collection and saves it to the local storage.
    Therefore, the HTML-code of https://earthview.withgoogle.com/ is parsed to read the location of the background-image. 
    """
    core.log(name, ["    Downloading the baseimage..."], "logging")
    path = "/data/wallpaper_background.png"
    try: 
        response = requests.get("https://earthview.withgoogle.com/")
    except Exception as e:
        print("-"*60)
        print("Exception in user code:")
        print("-"*60)
        traceback.print_exc(file=sys.stdout)
        print("-"*60)
        return {"processed":False, "value":e, "plugin": name}

    html = response.text
    regex = r"background-image: url\((?P<link>.+)\);"
    m = re.search(regex, html, re.IGNORECASE)
    if m:
        if m.group("link"):
            image_url = m.group("link")
        else: 
            image_url = None
            return {"processed": False, "value": "No URL found.", "plugin": name}
    else: 
        return {"processed": False, "value": "No URL found.", "plugin": name}
    core.log(name, ["    The URL is {}.".format(image_url),"    Downloading to {}...".format(core.global_variables.folder_base_short + path)], "logging")

    try: 
        f = open(core.global_variables.folder_base + path, "wb")
        f.write(requests.get(image_url).content)
        f.close()
    except Exception as e:
        print("-"*60)
        print("Exception in user code:")
        print("-"*60)
        traceback.print_exc(file=sys.stdout)
        print("-"*60)
        return {"processed": False, "value": "Error while downloading: {}".format(e), "plugin":name}

    core.log(name, ["    Download completed to {}.".format(core.global_variables.folder_base_short + path)], "logging")
    return {"processed": True, "value":core.global_variables.folder_base + path, "plugin":name}
    
def resize(im, size, offset=(0,0)):
    """
    This method is used to resize an image by cropping it or adding a black frame around it. 
    """
    bg = Image.new(im.mode, size)
    if im.size[0] < size[0]:
        factor_width = -1
    else:
        factor_width = 1
    if im.size[1] < size[1]:
        factor_height = -1
    else:
        factor_height = 1
    shift_left = factor_width * (((size[0] - im.size[0]) / 2) - offset[0])
    shift_top = factor_height * (((size[1] - im.size[1]) / 2) - offset[1])
    shift_right = size[0] - (factor_width * shift_left)
    shift_bottom = size[1] - (factor_height * shift_top)
    return im.crop((shift_left, shift_top, shift_right, shift_bottom))

def generate_wallpaper(background_path, mask_path, destination_path="/data/wallpaper.png"):
    """
    This method creates the actual wallpaper in several steps:
    
    1. Convert the Wallpaper to (almost) b/w and lighten it up a bit.
    2. Generate a set of normal and a bit smaller masks by basically resizing an Identicon to the size of the background and inverting it (to get a white on black and a black on white version). The different sizes will be used to place a colored overlay with a slightly brighter frame around it in the form of the Identicon ontop of the background.
    3. Create the overlay: It's a cutout from the original (colored) background with the form of the Identicon
    4. Create the frame: This does basically the same as 3.). The only difference is, that the cutout is brightened up a bit. 
    5. Create a dropshadow underneath the overlay.
    6. Merging the layers into one image.
    
    The final Image looks something like this:
    
        Overlay (colored)                                ____      ____      ____
        Frame (colored, lighter than the overlay)       ______    ______    ______
        Dropshadow                                     ________  ________  ________
        Background                                 ____________________________________

    """
    core.log(name, ["    Creating the final image..."], "info")
    
    framwewidth = 3

    #generate the background

    core.log(name, ["      Creating the background..."], "logging")
    bg_layer = Image.open(background_path)    #the background in color
    bg_layer = bg_layer.convert("RGBA")
    converter_color = ImageEnhance.Color(bg_layer)
    bg_layer = converter_color.enhance(0.05)
    converter_brightness = ImageEnhance.Brightness(bg_layer)
    bg_layer = converter_brightness.enhance(0.8)
    if DEBUG:
        core.log(name, ["      Saving the background..."], "debug")
        bg_layer.save(core.global_variables.folder_base_short + "/data/bg_layer.png")

    #generate the masks

    core.log(name, ["      Creating the normal masks..."], "logging")
    size = bg_layer.size
    mask_BoW = Image.open(mask_path)                                #"BoW" means black icon on white background.
    mask_WoB = ImageOps.invert(mask_BoW)                            #"WoB" is a white icon on black bg.
    if not mask_BoW.size == size:
        mask_WoB = resize(mask_WoB, size)
        mask_BoW = ImageOps.invert(mask_WoB)
    mask_WoB = mask_WoB.convert("1")
    mask_BoW = mask_BoW.convert("1")
    if DEBUG:
        core.log(name, ["      Saving the normal masks..."], "debug")
        mask_WoB.save(core.global_variables.folder_base + "/data/mask_WoB.png")
        mask_BoW.save(core.global_variables.folder_base + "/data/mask_BoW.png")

    core.log(name, ["      Creating the small masks..."], "info")
    mask_WoB_small = mask_WoB.convert("RGB")

    offset_layers = []
    offset_layer1 = Image.new("RGB", size)
    offset_layer1.paste(ImageChops.offset(mask_WoB_small, framwewidth, framwewidth))
    offset_layer1 = offset_layer1.convert("1")
    offset_layer2 = Image.new("RGB", size)
    offset_layer2.paste(ImageChops.offset(mask_WoB_small, -framwewidth, framwewidth))
    offset_layer2 = offset_layer2.convert("1")
    offset_layer3 = Image.new("RGB", size)
    offset_layer3.paste(ImageChops.offset(mask_WoB_small, -framwewidth, -framwewidth))
    offset_layer3 = offset_layer3.convert("1")
    offset_layer4 = Image.new("RGB", size)
    offset_layer4.paste(ImageChops.offset(mask_WoB_small, framwewidth, -framwewidth))
    offset_layer4 = offset_layer4.convert("1")

    mask_WoB_small = mask_WoB_small.convert("1")
    mask_WoB_small = ImageChops.logical_and(mask_WoB_small, offset_layer1)
    mask_WoB_small = ImageChops.logical_and(mask_WoB_small, offset_layer2)
    mask_WoB_small = ImageChops.logical_and(mask_WoB_small, offset_layer3)
    mask_WoB_small = ImageChops.logical_and(mask_WoB_small, offset_layer4)

    mask_BoW_small = ImageOps.invert(mask_WoB_small.convert("RGB"))
    mask_BoW_small = mask_BoW_small.convert("1")
    if DEBUG:
        core.log(name, ["      Saving the small masks..."], "debug")
        mask_WoB_small.save(core.global_variables.folder_base + "/data/mask_WoB_small.png")
        mask_BoW_small.save(core.global_variables.folder_base + "/data/mask_BoW_small.png")


    #generate the colored overlay

    core.log(name, ["      Creating the colored overlay..."], "logging")
    overlay_layer = Image.open(background_path)
    overlay_layer.putalpha(mask_WoB_small)
    if DEBUG:
        core.log(name, ["      Saving the colored overlay..."], "debug")
        overlay_layer.save(core.global_variables.folder_base + "/data/overlay_layer.png")

    #generate the frame around the colored overlay

    core.log(name, ["      Creating the frame around the overlay..."], "logging")
    frame_layer = Image.open(background_path)
    frame_layer = Image.blend(Image.new("RGB", size, "white"), frame_layer, 0.65)
    frame_layer.putalpha(mask_WoB)
    if DEBUG:
        core.log(name, ["      Saving the frame..."], "debug")
        frame_layer.save(core.global_variables.folder_base + "/data/frame_layer.png")

    #generate the shadow

    core.log(name, ["      Creating the dropshadow..."], "logging")
    shadow_layer =  mask_BoW.convert("RGBA")
    shadow_layer.putalpha(mask_WoB)
    """
    A copy if the mask is pasted ontop of itself with a 2px offset into the 4 diagonal directions each to increase it's size into each direction. (The shadow would otherwise disappear behind the colored overlay.)
    The whole layer is then blurred multiple times to increase the blur's effect.
    Finally, the shadow_layer is blended with a completely transparent layer to add some transparency to it.
    """
    
    offset_layers = []
    offsets = [(1,1),(-1,1),(1,0),(-1,0)]
    for (x, y) in offsets:
        offset_layers.append(ImageChops.offset(shadow_layer, x, y))
    for offset_layer in offset_layers:
        shadow_layer.paste(offset_layer, None, offset_layer)
    
    core.log(name, ["        Blurring the shadow..."], "logging")
    for n in range(3):      #as noted above, the Blur is applied multiple times for a stronger effect. 3 has proven as a good compromise between a good effect and not too much necessary calculation.
        core.log(name, ["          Step {}/{}.".format(n + 1, 3)], "logging")
        shadow_layer = shadow_layer.filter(ImageFilter.BLUR)
    core.log(name, ["        Adding transparency..."], "logging")
    shadow_layer = Image.blend(Image.new("RGBA", size), shadow_layer, 0.8)
    if DEBUG:
        core.log(name, ["      Saving the dropshadow..."], "debug")
        shadow_layer.save(core.global_variables.folder_base + "/data/shadow_layer.png")

    #merge the shadow with the background
    
    """
    This will add the shadow manually to the background image. Usign PIL's merge() or composite_alpha() was causing the image underneath the shadow to turn greyish which looked pretty ugly on dark parts of the image.
    To prevent this behaviour, this tool iterates over the pixels of the whole image and changes the colorvalues according to the alphavalue of the corresponding image in the mask.
    If the pixel in the mask is completely transparent (a_mask == 0) the calculation will be skipped and the original pixel won't be changed. If the pixel in the mask is completely opaque (a_mask == 255) the pixel in the original image will be turned black. For every other alpha value the new color is calculated via new = old * (1 - (a_mask / 255)).
    """
    core.log(name, ["      Merging the shadow with the background..."], "logging")
    try:
        pixels_changed_count = 0
        pixels_bg = bg_layer.load()
        pixels_mask = shadow_layer.load()
        for x in range(bg_layer.size[0]):
            for y in range(bg_layer.size[1]):
                r_mask, g_mask, b_mask, a_mask = pixels_mask[x, y]
                if 0 < a_mask < 255:
                    r_bg, g_bg, b_bg, a_bg = pixels_bg[x, y]
                    factor = (1.0 - (float(a_mask) / 255.0))
                    r_bg = int(float(r_bg) * factor)
                    g_bg = int(float(g_bg) * factor)
                    b_bg = int(float(b_bg) * factor)
                    pixels_bg[x, y] = (r_bg, g_bg, b_bg, a_bg)
                    pixels_changed_count += 1
                elif a_mask == 255:
                    a_bg = pixels_bg[x, y][-1]
                    pixels_bg[x, y] = (0, 0, 0, a_bg)
                    pixels_changed_count += 1
    except Exception as e:
        print("-"*60)
        print("Exception in user code:")
        print("-"*60)
        traceback.print_exc(file=sys.stdout)
        print("-"*60)
        return {"processed": False, "value": e, "plugin": name}
    finally: 
        core.log(name, ["        {} out of {} pixels processed.".format(pixels_changed_count, bg_layer.size[0] * bg_layer.size[1])], "logging")
    if DEBUG:
        core.log(name, ["      Saving the background and shadow..."], "debug")
        bg_layer.save(core.global_variables.folder_base + "/data/bg_layer_shadow.png")

    #merge the layers
    
    core.log(name, ["      Merging the layers..."], "logging")
    final = Image.new("RGBA", size)
    final.paste(bg_layer)
    final.paste(frame_layer, None, frame_layer)
    final.paste(overlay_layer, None, overlay_layer)
    final.save(core.global_variables.folder_base + destination_path)
    core.log(name, ["    Created the wallpaper at {}.".format(core.global_variables.folder_base_short + destination_path)], "info")
    return {"processed": True, "value": core.global_variables.folder_base + destination_path, "plugin": name}

def process(key, params):
    try:
        if key in ["schedule_day", "set_wallpaper", "wallpaper"]:
            core.log(name, ["  Generating and setting a new wallpaper..."], "info")
            wallpaper_bg = get_wallpaper()
            if wallpaper_bg["processed"]:
                identicon = core.process(key="identicon", params=[str(time.time())], origin=name, target="Identicon")[0]
                if identicon["processed"]:
                    wallpaper = generate_wallpaper(wallpaper_bg["value"], identicon["value"])
                    if key == "wallpaper":
                        return wallpaper
                    elif wallpaper["processed"]:
                        result = core.process("ar_file", ["g2", "wallpaper.set", wallpaper["value"]])
                        return result
                    else:
                        return wallpaper
                else: 
                    return identicon
            else:
                return wallpaper_bg
        else:
            return {"processed": False, "value": "Keyword not in use. ({}, {})".format(key, params), "plugin": name}
    except Exception as e:
        print("-"*60)
        print("Exception in user code:")
        print("-"*60)
        traceback.print_exc(file=sys.stdout)
        print("-"*60)
        core.log(name, ["{}".format(e)], "error")
        return {"processed": False, "value": e, "plugin": name}
