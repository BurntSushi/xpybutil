import xcb.xproto
from PIL import Image

def net_wm_icon_to_bgra(data):
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

def color_humanize(clr):
    t = hex(clr).replace('0x', '')
    return '#%s' % ('0' * (6 - len(t)) + t)

def hex_to_rgb(h):
    s = color_humanize(h)
    return (int(s[1:3], 16), int(s[3:5], 16), int(s[5:7], 16))

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

