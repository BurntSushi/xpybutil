# This code was ported from the xcb-util package (an ancillary
# package to the X C Binding) by Andrew Gallant. The original
# source code can be found here:
# http://cgit.freedesktop.org/xcb/util/tree/renderutil/util.c
#
# Note: This *should* be a complete port.

import xcb, xcb.xproto, xcb.render

ID = 1 << 0
TYPE = 1 << 1
DEPTH = 1 << 2
RED = 1 << 3
RED_MASK = 1 << 4
GREEN = 1 << 5
GREEN_MASK = 1 << 6
BLUE = 1 << 7
BLUE_MASK = 1 << 8
ALPHA = 1 << 9
ALPHA_MASK = 1 << 10
COLORMAP = 1 << 11

ARGB_32 = 0
RGB_24 = 1
A_8 = 2
A_4 = 3
A_1 = 4

standardFormats = [
    # ARGB_32
    {
        'template': {
            'id': 0,
            'type': xcb.render.PictType.Direct,
            'depth': 32,
            'direct': {
                'red': 16,
                'red_mask': 0xff,
                'green': 8,
                'green_mask': 0xff,
                'blue': 0,
                'blue_mask': 0xff,
                'alpha': 24,
                'alpha_mask': 0xff
            },
            'colormap': 0
        },

        'mask': (TYPE | DEPTH | RED | RED_MASK | GREEN | GREEN_MASK | BLUE |
                 BLUE_MASK | ALPHA | ALPHA_MASK)
    },

    # RGB_24
    {
        'template': {
            'id': 0,
            'type': xcb.render.PictType.Direct,
            'depth': 24,
            'direct': {
                'red': 16,
                'red_mask': 0xff,
                'green': 8,
                'green_mask': 0xff,
                'blue': 0,
                'blue_mask': 0xff,
                'alpha': 0,
                'alpha_mask': 0x00
            },
            'colormap': 0
        },

        'mask': (TYPE | DEPTH | RED | RED_MASK | GREEN | GREEN_MASK | BLUE |
                 BLUE_MASK | ALPHA_MASK)
    },

    # A_8
    {
        'template': {
            'id': 0,
            'type': xcb.render.PictType.Direct,
            'depth': 8,
            'direct': {
                'red': 0,
                'red_mask': 0x00,
                'green': 0,
                'green_mask': 0x00,
                'blue': 0,
                'blue_mask': 0x00,
                'alpha': 0,
                'alpha_mask': 0xff
            },
            'colormap': 0
        },

        'mask': (TYPE | DEPTH | RED_MASK | GREEN_MASK | BLUE_MASK | ALPHA |
                 ALPHA_MASK)
    },

    # A_4
    {
        'template': {
            'id': 0,
            'type': xcb.render.PictType.Direct,
            'depth': 4,
            'direct': {
                'red': 0,
                'red_mask': 0x00,
                'green': 0,
                'green_mask': 0x00,
                'blue': 0,
                'blue_mask': 0x00,
                'alpha': 0,
                'alpha_mask': 0x0f
            },
            'colormap': 0
        },

        'mask': (TYPE | DEPTH | RED_MASK | GREEN_MASK | BLUE_MASK | ALPHA |
                 ALPHA_MASK)
    },

    # A_1
    {
        'template': {
            'id': 0,
            'type': xcb.render.PictType.Direct,
            'depth': 1,
            'direct': {
                'red': 0,
                'red_mask': 0x00,
                'green': 0,
                'green_mask': 0x00,
                'blue': 0,
                'blue_mask': 0x00,
                'alpha': 0,
                'alpha_mask': 0x01
            },
            'colormap': 0
        },

        'mask': (TYPE | DEPTH | RED_MASK | GREEN_MASK | BLUE_MASK | ALPHA |
                 ALPHA_MASK)
    }
]

def find_visual_format(formats, visid):
    for screen in formats.screens:
        for depth in screen.depths:
            for visual in depth.visuals:
                if visual.visual == visid:
                    return visual

def find_format(formats, mask, template, count):
    if not formats:
        return None

    for format in formats.formats:
        if mask & ID:
            if template['id'] != format.id:
                continue
        if mask & TYPE:
            if template['type'] != format.type:
                continue
        if mask & DEPTH:
            if template['depth'] != format.depth:
                continue
        if mask & RED:
            if template['direct']['red'] != format.direct.red_shift:
                continue
        if mask & RED_MASK:
            if template['direct']['red_mask'] != format.direct.red_mask:
                continue
        if mask & GREEN:
            if template['direct']['green'] != format.direct.green_shift:
                continue
        if mask & GREEN_MASK:
            if template['direct']['green_mask'] != format.direct.green_mask:
                continue
        if mask & BLUE:
            if template['direct']['blue'] != format.direct.blue_shift:
                continue
        if mask & BLUE_MASK:
            if template['direct']['blue_mask'] != format.direct.blue_mask:
                continue
        if mask & ALPHA:
            if template['direct']['alpha'] != format.direct.alpha_shift:
                continue
        if mask & ALPHA_MASK:
            if template['direct']['alpha_mask'] != format.direct.alpha_mask:
                continue
        if mask & COLORMAP:
            if template['colormap'] != format.colormap:
                continue

        if not count:
            return format
        count -= 1

    return None

def find_standard_format(formats, format):
    if format < 0 or format >= len(standardFormats):
        return None

    return find_format(
        formats,
        standardFormats[format]['mask'],
        standardFormats[format]['template'],
        0
    )
