#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PIL import Image, ImageFilter, ImageOps, ImageChops, ImageEnhance

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

def generate(background_path, mask_path, final_path):

    #generate the background

    #print("Creating the background")
    """
    First of all, the background layer is created. It contains the 
    """
    bg_layer = Image.open(background_path)    #the background in color
    converter_color = ImageEnhance.Color(bg_layer)
    converter_brightness = ImageEnhance.Brightness(bg_layer)
    bg_layer = converter_color.enhance(0.05)
    bg_layer = converter_brightness.enhance(0.8)
    #bg_layer.convert("L")
    #bg_layer.save("./bg_layer.png")

    #generate the mask

    #print("Creating the mask")
    size = bg_layer.size
    mask_BoW = Image.open(mask_path)    #"BoW" means black icon on white background. "WoB" is a white icon on black bg.
    mask_WoB = ImageOps.invert(mask_BoW)
    if not mask_BoW.size == size:
        mask_WoB = resize(mask_WoB, size)
        mask_BoW = ImageOps.invert(mask_WoB)
    mask_WoB = mask_WoB.convert("1")
    mask_BoW = mask_BoW.convert("1")
    #mask_WoB.save("./mask_WoB.png")
    #mask_BoW.save("./mask_BoW.png")

    #generate the overlay

    #print("Creating the overlay")
    overlay_layer = Image.open(background_path)    #the overlay, black on white
    overlay_layer.putalpha(mask_WoB)
    #overlay_layer.save("./overlay_layer.png")

    #generate the shadow

    #print("Creating the dropshadow")
    shadow_layer =  mask_BoW.convert("RGBA")
    shadow_layer.putalpha(mask_WoB)
    """
    A copy if the image is pasted ontop of it with a 2px offset into the 4 diagonal directions to increase it's size.
    Otherwise the shadow would disappear behind the colored overlay.
    The whole layer is then blurred multiple times to increase the blur's effect.
    Finally, the shadow-layer is blended with a completely transparent layer to add some transparency.
    """
    offset_layers = []
    offsets = [(2,2),(-2,2),(2,-2),(-2,-2)]
    for (x, y) in offsets:
        offset_layers.append(ImageChops.offset(shadow_layer, x, y))
    for offset_layer in offset_layers:
        shadow_layer.paste(offset_layer, None, offset_layer)
    #print("Blurring the shadow")
    n = 0
    while n < 5:    #as noted above, the Blur is applied multiple times for a stronger effect.
        shadow_layer = shadow_layer.filter(ImageFilter.BLUR)
        n += 1
    #print("Adding transparency")
    shadow_layer = Image.blend(Image.new("RGBA", size), shadow_layer, 0.7)
    #shadow_layer.save("./shadow_layer.png")

    '''
    #generate the light frame
    frame_layer = overlay_layer.filter(ImageFilter.FIND_EDGES)
    frame_layer.save("./frame_layer.png")
    '''
    
    #merge the layers
    
    #print("Creating the final image")
    final = Image.new("RGBA", size)
    final.paste(bg_layer.convert("L"))
    final.paste(shadow_layer, None, shadow_layer)
    final.paste(overlay_layer, None, overlay_layer)
    final.save(final_path)
    
if __name__ == '__main__':
    generate("./img.jpg", "./identicon.png", "./wallpaper.png")