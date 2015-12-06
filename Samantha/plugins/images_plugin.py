#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re, pydenticon, core, time, global_variables, requests, cloudinary
from PIL import Image, ImageChops, ImageEnhance, ImageFilter, ImageOps

is_sam_plugin = 1
name = "Images"
keywords = ["identicon", "schedule_h", "wallpaper"]
has_toggle = 0
has_set = 0

DEBUG = 1


def initialize():
    core.log(name, "Startup")
    core.log(name, "Hello World!")

def stop():
    core.log(name, "I'm not even running anymore!")

def get_wallpaper():
    core.log(name, "    Downloading the baseimage.")
    path = "/data/wallpaper_background.png"
    response = requests.get("https://earthview.withgoogle.com/")
    html = response.text
    regex = r"background-image: url\((?P<link>.+)\);"
    m = re.search(regex, html, re.IGNORECASE)
    if m:
        if m.group("link"):
            image_url = m.group("link")
        else: 
            image_url = None
    else: 
        image_url = None
    core.log(name, "    The URL is {}. Downloading to {}.".format(image_url, global_variables.folder_base + path))
    
    if image_url:
        f = open(global_variables.folder_base + path, "wb")
        f.write(requests.get(image_url).content)
        f.close()
    else: 
        core.log(name, "    Error: Download not completed.")
    core.log(name, "    Download completed to {}.".format(global_variables.folder_base + path))
    return path
    
def resize(im, size, offset=(0,0)):
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

    core.log(name, "    Creating the final image")

    #generate the background

    core.log(name, "      Creating the background")
    bg_layer = Image.open(global_variables.folder_base + background_path)    #the background in color
    bg_layer = bg_layer.convert("RGBA")
    converter_color = ImageEnhance.Color(bg_layer)
    bg_layer = converter_color.enhance(0.05)
    converter_brightness = ImageEnhance.Brightness(bg_layer)
    bg_layer = converter_brightness.enhance(0.8)
    if DEBUG:
        core.log(name, "      DEBUG: Saving the background")
        bg_layer.save(global_variables.folder_base + "/data/bg_layer.png")

    #generate the masks

    core.log(name, "      Creating the normal masks")
    size = bg_layer.size
    mask_BoW = Image.open(global_variables.folder_base + mask_path)     #"BoW" means black icon on white background.
    mask_WoB = ImageOps.invert(mask_BoW)                                #"WoB" is a white icon on black bg.
    if not mask_BoW.size == size:
        mask_WoB = resize(mask_WoB, size)
        mask_BoW = ImageOps.invert(mask_WoB)
    mask_WoB = mask_WoB.convert("1")
    mask_BoW = mask_BoW.convert("1")
    if DEBUG:
        core.log(name, "      DEBUG: Saving the normal masks")
        mask_WoB.save(global_variables.folder_base + "/data/mask_WoB.png")
        mask_BoW.save(global_variables.folder_base + "/data/mask_BoW.png")
    '''
    core.log(name, "      Creating the big masks")
    mask_BoW_big = mask_BoW.convert("RGBA")
    mask_BoW_big.putalpha(mask_WoB)
    offset_layers = []
    offsets = [(2,2),(-2,2),(2,-2),(-2,-2)]
    for (x, y) in offsets:
        offset_layers.append(ImageChops.offset(mask_BoW_big, x, y))
    for offset_layer in offset_layers:
        mask_BoW_big.paste(offset_layer, None, offset_layer)
    mask_WoB_big = ImageOps.invert(mask_BoW_big)
    mask_WoB_big = mask_WoB_big.convert("1")
    mask_BoW_big = mask_BoW_big.convert("1")
    if DEBUG:
        core.log(name, "      DEBUG: Saving the big masks")
        mask_WoB_big.save(global_variables.folder_base + "/data/mask_WoB_big.png")
        mask_BoW_big.save(global_variables.folder_base + "/data/mask_BoW_big.png")
    '''
    #generate the colored overlay

    core.log(name, "      Creating the colored overlay")
    overlay_layer = Image.open(global_variables.folder_base + background_path)
    overlay_layer.putalpha(mask_WoB)
    if DEBUG:
        core.log(name, "      DEBUG: Saving the colored overlay")
        overlay_layer.save(global_variables.folder_base + "/data/overlay_layer.png")

    #generate the frame around the colored overlay
    '''
    core.log(name, "      Creating the frame around the overlay")
    frame_layer = Image.open(global_variables.folder_base + background_path)
    frame_layer = Image.blend(Image.new("RGBA", size, "white"), frame_layer, 0.8)
    frame_layer.putalpha(mask_WoB_big)
    if DEBUG:
        core.log(name, "      DEBUG: Saving the frame")
        frame_layer.save(global_variables.folder_base + "/data/frame_layer.png")
    '''
    #generate the shadow

    core.log(name, "      Creating the dropshadow")
    shadow_layer =  mask_BoW_big.convert("RGBA")
    shadow_layer.putalpha(mask_WoB_big)
    """
    A copy if the mask is pasted ontop of itself with a 2px offset into the 4 diagonal directions each to increase it's size into each direction. (The shadow would otherwise disappear behind the colored overlay.)
    The whole layer is then blurred multiple times to increase the blur's effect.
    Finally, the shadow_layer is blended with a completely transparent layer to add some transparency to it.
    """
    
    offset_layers = []
    offsets = [(1,1),(-1,1),(1,-1),(-1,-1)]
    for (x, y) in offsets:
        offset_layers.append(ImageChops.offset(shadow_layer, x, y))
    for offset_layer in offset_layers:
        shadow_layer.paste(offset_layer, None, offset_layer)
    
    core.log(name, "      Blurring the shadow")
    for n in range(3):      #as noted above, the Blur is applied multiple times for a stronger effect. 3 has proven as a good compromise between a good effect and not too much necessary calculation.
        core.log(name, "        Step {}/{}".format(n + 1, 3))
        shadow_layer = shadow_layer.filter(ImageFilter.BLUR)
    core.log(name, "      Adding transparency")
    shadow_layer = Image.blend(Image.new("RGBA", size), shadow_layer, 0.8)
    if DEBUG:
        core.log(name, "      DEBUG: Saving the dropshadow")
        shadow_layer.save(global_variables.folder_base + "/data/shadow_layer.png")

    #merge the shadow with the background
    
    """
    This will add the shadow manually to the background image. Usign PIL's merge() or composite_alpha() was causing the image underneath the shadow to turn greyish which looked pretty ugly on dark parts of the image.
    To prevent this behaviour, this tool iterates over the pixels of the whole image and changes the colorvalues according to the alphavalue of the corresponding image in the mask.
    If the pixel in the mask is completely transparent (a_mask == 0) the calculation will be skipped and the original pixel won't be changed. If the pixel in the mask is completely opaque (a_mask == 255) the pixel in the original image will be turned black. For every other alpha value the new color is calculated via new = old * (1 - (a_mask / 255)).
    """
    core.log(name, "      Merging the shadow with the background")
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
        core.log(name, "Error: {}".format(e))
    finally: 
        core.log(name, "      {} out of {} pixels processed.".format(pixels_changed_count, bg_layer.size[0] * bg_layer.size[1]))
    if DEBUG:
        core.log(name, "      DEBUG: Saving the background+shadow")
        bg_layer.save(global_variables.folder_base + "/data/bg_layer_shadow.png")
    '''
    #generate the light frame
    frame_layer = overlay_layer.filter(ImageFilter.FIND_EDGES)
    frame_layer.save("./frame_layer.png")
    '''
    #merge the layers
    
    core.log(name, "      Merging the layers")
    final = Image.new("RGBA", size)
    final.paste(bg_layer)
    final.paste(frame_layer, None, frame_layer)
    final.paste(overlay_layer, None, overlay_layer)
    final.save(global_variables.folder_base + destination_path)
    core.log(name, "    Created the wallpaper at {}.".format(global_variables.folder_base + destination_path))
    return destination_path

def generate_identicon(data="I'm Samantha", path="/data/identicon.png"):
    """
    generates an identicon and sends it to the G2
    possibly via an AutoRemote Plugin?
    """
    core.log(name, "    Generating the Identicon.")
    generator = pydenticon.Generator(5, 5)
    identicon = generator.generate(data, 300, 300)
    core.log(name, "    Generated the Identicon. Saving at {}.".format(global_variables.folder_base + path))
    f = open(global_variables.folder_base + path, "wb")
    f.write(identicon)
    f.close()
    core.log(name, "    Generated the Identicon at {}.".format(global_variables.folder_base + path))
    return path

def process(key, param, comm):
    try:
        if key == "schedule_h":
            if param == "0":
                core.log(name, "  Generating the daily wallpaper.")
                wallpaper_bg = get_wallpaper()
                identicon = generate_identicon(str(time.time()))
                wallpaper = generate_wallpaper(wallpaper_bg, identicon)
            else:
                core.log(name, "  Warning: parameter {} not in use.".format(param))
        elif key == "wallpaper":
            core.log(name, "  Generating a new wallpaper.")
            wallpaper_bg = get_wallpaper()
            identicon = generate_identicon(str(time.time()))
            wallpaper = generate_wallpaper(wallpaper_bg, identicon)
        elif key == "identicon":
            core.log(name, "  Generating an Identicon with the data '{}'.".format(param))
            if param:
                generate_identicon(param)
            else:
                generate_identicon()
        else:
            core.log(name, "  Warning: parameter {} not in use.".format(param))
    except Exception as e:
        core.log(name, "Error: {}".format(e))