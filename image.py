import xcb.xproto
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

def get_image(width, height, data):
    im = Image.fromstring('RGBA', (width, height),
                          ''.join([chr(i) for i in data]), 'raw', 'BGRA')

    return im

def get_data(image):
    return [ord(s) for s in image.tostring('raw', 'BGRA')]

def get_image_from_pixmap(c, pid):
    try:
        geom = c.core.GetGeometry(pid).reply()
        pimg = c.core.GetImage(xcb.xproto.ImageFormat.ZPixmap, pid,
                               0, 0, geom.width, geom.height,
                               2**32 - 1).reply().data

        return geom.width, geom.height, pimg
    except xcb.xproto.BadDrawable:
        return 0, 0, []

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
    s = '%s%s' % (hex(h), '0' * (8 - len(hex(h))))
    return (int(s[2:4], 16), int(s[4:6], 16), int(s[6:8], 16))

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

def blend_bgcolor(data, color, width, height, has_alpha=False):
    assert width > 0 and height > 0
    assert data

    im = Image.new('RGBA', (width, height))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, width, height], fill=parse_color(color))
    bg = get_data(im)

    ret = []
    for pixel in xrange(0, len(data), 4):
        blue = data[pixel]
        green = data[pixel + 1]
        red = data[pixel + 2]
        alpha = data[pixel + 3]

        if not has_alpha and not blue and not green and not red:
            blue = bg[pixel]
            green = bg[pixel + 1]
            red = bg[pixel + 2]

        if has_alpha:
            blue = bg[pixel] + (((blue - bg[pixel]) * alpha) >> 8)
            green = bg[pixel + 1] + (((green - bg[pixel + 1]) * alpha) >> 8)
            red = bg[pixel + 2] + (((red - bg[pixel + 2]) * alpha) >> 8)

        ret.append(blue)
        ret.append(green)
        ret.append(red)
        ret.append(alpha)

    return ret

def blend(c, data, bg_drawable, width, height, x, y, has_alpha=False):
    assert width > 0 and height > 0
    assert data

    ret = []
    bg = c.core.GetImage(xcb.xproto.ImageFormat.ZPixmap, bg_drawable,
                         x, y, width, height,
                         2**32 - 1).reply().data

    for pixel in xrange(0, len(data), 4):
        blue = data[pixel]
        green = data[pixel + 1]
        red = data[pixel + 2]
        alpha = data[pixel + 3]

        if not has_alpha and not blue and not green and not red:
            blue = bg[pixel]
            green = bg[pixel + 1]
            red = bg[pixel + 2]

        if has_alpha:
            blue = bg[pixel] + (((blue - bg[pixel]) * alpha) >> 8)
            green = bg[pixel + 1] + (((green - bg[pixel + 1]) * alpha) >> 8)
            red = bg[pixel + 2] + (((red - bg[pixel + 2]) * alpha) >> 8)

        ret.append(blue)
        ret.append(green)
        ret.append(red)
        ret.append(alpha)

    return ret
