#ant1 201410
#Support functions for image display in Planets4X game

from PIL import Image

def ColorAsAlpha(im, colorin, alphalevel):
    ''' im is PIL RGBA image, color is color index or RGB or RGBA.
    ant1 20100826'''
    k = []
    for i in im.getdata():
        match = True
        for j in range(3):
            if i[j] != colorin[j]:
                match = False
        if match:
            i = (i[0], i[1], i[2], alphalevel)
        k.append(i)
    im.putdata(k)
    return im

def ColorSwitch(im, colorin, colorout):
    ''' im is PIL RGBA image, color is color index or RGB or RGBA.
    ant1 20141028'''
    k = []
    for i in im.getdata():
        match = True
        for j in range(3):
            if i[j] != colorin[j]:
                match = False
        if match:
            if im.mode == "RGBA":
                i = (colorout[0], colorout[1], colorout[2], colorin[3])
            elif im.mode == "RGB":
                i = (colorout[0], colorout[1], colorout[2])                
        k.append(i)
    im.putdata(k)
    return im

def MainColor(im):
    if im.format != 'RGBA': im.convert('RGBA')
    appear = 0
    main_color = 0
    for i in im.getcolors():
        if appear < i[0]:
            appear = i[0]
            main_color = i[1]
    return main_color

def fit_textinbox(string, box_size, font, font_size):
    ''' string, tuplet, font file ex:'arialdb.ttf, integer
    string is string to be printed
    box_size : size in pixels of the area wherestring should fit
    font : truetype/opentype file to be used, ex: 'arialbd.ttf'
    font_size : initial guess for size of the font, integer
    ant1 20100822'''
    try:
        f = ImageFont.truetype(font, font_size)
        w,h = f.getsize(string)
        while (w>box_size[0] or h>box_size[1]) and font_size>3:
            font_size-=1
            f = ImageFont.truetype(font, font_size)
            w,h = f.getsize(string)
        if (w>box_size[0] or h>box_size[1]) and font_size==3: f = ImageFont.load_default()
    except: 
        f = ImageFont.load_default()
    return f

def DisplayZoom( im, fact ):
    if fact<1: fact=1
#    if im.size[0]*int(fact)>760: fact=int(760/im.size[0])
    for i, s in enumerate(["1", "L", "P"]):
        if im.mode in s:
            im = im.convert("RGB")
    if fact==1: Xim=im.copy()
    else:
        Xim = Image.new(im.mode, (im.size[0]*int(fact), im.size[1]*int(fact)) )
        for w in range(im.size[0]):
            for h in range(im.size[1]):
                for f in range(int(fact)):
                    for g in range(int(fact)):
                        Xim.putpixel((w*int(fact)+f, h*int(fact)+g), im.getpixel((w,h)))
    return Xim

        








    
    
