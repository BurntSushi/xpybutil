import xcb.xproto
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

def parse_net_wm_icon(data):
    ret = []
    for i, d in enumerate(data):
        pixel = i * 4

        alpha = d >> 24
        red = ((alpha << 24) ^ d) >> 16
        green = (((alpha << 24) + (red << 16)) ^ d) >> 8
        blue = (((alpha << 24) + (red << 16) + (green << 8)) ^ d) >> 0

        ret.append(blue)
        ret.append(green)
        ret.append(red)
        ret.append(alpha)

    return ret

def parse_color(clr):
    t = hex(clr).replace('0x', '')
    return '#%s' % ('0' * (6 - len(t)) + t)

def hex_to_rgb(h):
    #s = '0x%s%s' % ('0' * (8 - len(hex(h))), hex(h))
    s = parse_color(h)
    return (int(s[1:3], 16), int(s[3:5], 16), int(s[5:7], 16))

def border(border_color, bg_color, width, height, orient):
    assert ((width == 1 and orient in ('top', 'bottom')) or
            (height == 1 and orient in ('left', 'right')))

    im = Image.new('RGBA', (width, height))
    bg = (max(width, height) - 1) * [hex_to_rgb(bg_color)]
    border = [hex_to_rgb(border_color)]

    if orient in ('bottom', 'right'):
        data = bg + border
    else:
        data = border + bg

    im.putdata(data)

    return get_data(im)

def corner(border_color, bg_color, width, height, orient):
    im = Image.new('RGBA', (width, height))
    d = ImageDraw.Draw(im)

    d.rectangle([0, 0, width, height], fill=hex_to_rgb(bg_color))
    coords = None

    w, h = width, height
    if orient in ('top_left', 'left_top'):
        coords = [(0, h), (0, 0), (w, 0)]
    elif orient in ('top_right', 'right_top'):
        coords = [(0, 0), (w - 1, 0), (w - 1, h)]
    elif orient in ('right_bottom', 'bottom_right'):
        coords = [(w - 1, 0), (w - 1, h - 1), (0, h - 1)]
    elif orient in ('bottom_left', 'left_bottom'):
        coords = [(0, 0), (0, h - 1), (w - 1, h - 1)]

    assert coords is not None

    d.line(coords, fill=hex_to_rgb(border_color))

    return get_data(im)

def box(color, width, height):
    im = Image.new('RGBA', (width, height))
    d = ImageDraw.Draw(im)

    d.rectangle([0, 0, width, height], fill=parse_color(color))

    return get_data(im)

def draw_text_bgcolor(text, font, size, color_bg, color_text, max_width,
                      max_height):
    f = ImageFont.truetype(font, size, encoding='unic')
    fw, fh = f.getsize(unicode(text, 'utf-8'))

    w, h = min(fw, max_width), min(fh, max_height)

    im = Image.new('RGBA', (w, h))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, w, h], fill=parse_color(color_bg))
    d.text((0, 0), unicode(text, 'utf-8'), font=f,
           fill=parse_color(color_text))

    return get_data(im), w, h

def get_image_from_pixmap(c, pid):
    try:
        geom = c.core.GetGeometry(pid).reply()
        pimg = c.core.GetImage(xcb.xproto.ImageFormat.ZPixmap, pid,
                               0, 0, geom.width, geom.height,
                               2**32 - 1).reply().data

        return geom.width, geom.height, pimg
    except xcb.xproto.BadDrawable:
        return 0, 0, []

def get_image(width, height, data):
    im = Image.fromstring('RGBA', (width, height),
                          ''.join([chr(i) for i in data]), 'raw', 'BGRA')

    return im

def get_bitmap(width, height, data):
    im = Image.fromstring('1', (width, height),
                          ''.join([chr(i) for i in data]), 'raw', '1;R')

    return im

def get_data(image):
    return [ord(s) for s in image.tostring('raw', 'BGRA')]

def blend(img, mask, color, width, height, alpha=1):
    assert width > 0 and height > 0

    bg = Image.new('RGBA', (width, height))
    bgd = ImageDraw.Draw(bg)
    bgd.rectangle([0, 0, width, height], fill=parse_color(color))
    bg2 = bg.copy()

    blended = Image.composite(img, bg, mask)
    blended = Image.blend(bg2, blended, alpha)

    return get_data(blended)
