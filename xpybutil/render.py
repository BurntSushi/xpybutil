"""
I once used the help of this module to implement a basic compositing manager
using xpyb. It only did transparency, and not well. (Performance was actually
quite nice.) It's called pycompmgr.

This is meant to be a very close translation to the corresponding xcb-util
module. Mostly because I lack a deep understanding of everything here.
"""
from xpybutil.compat import render

class PictFormat:
    Id = 1
    Type = 2
    Depth = 4
    Red = 8
    RedMask = 16
    Green = 32
    GreenMask = 64
    Blue = 128
    BlueMask = 256
    Alpha = 512
    AlphaMask = 1024
    Colormap = 2048

class PictStandard:
    Argb32 = 0
    Rgb24 = 1
    A8 = 2
    A4 = 3
    A1 = 4

standardFormats = [
    # ARGB_32
    {
        'template': {
            'id': 0,
            'type': render.PictType.Direct,
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

        'mask': (PictFormat.Type | PictFormat.Depth | PictFormat.Red |
                 PictFormat.RedMask | PictFormat.Green | PictFormat.GreenMask |
                 PictFormat.Blue | PictFormat.BlueMask | PictFormat.Alpha |
                 PictFormat.AlphaMask)
    },

    # RGB_24
    {
        'template': {
            'id': 0,
            'type': render.PictType.Direct,
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

        'mask': (PictFormat.Type | PictFormat.Depth | PictFormat.Red |
                 PictFormat.RedMask | PictFormat.Green | PictFormat.GreenMask |
                 PictFormat.Blue | PictFormat.BlueMask | PictFormat.AlphaMask)
    },

    # A_8
    {
        'template': {
            'id': 0,
            'type': render.PictType.Direct,
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

        'mask': (PictFormat.Type | PictFormat.Depth | PictFormat.RedMask |
                 PictFormat.GreenMask | PictFormat.BlueMask |
                 PictFormat.Alpha | PictFormat.AlphaMask)
    },

    # A_4
    {
        'template': {
            'id': 0,
            'type': render.PictType.Direct,
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

        'mask': (PictFormat.Type | PictFormat.Depth | PictFormat.RedMask |
                 PictFormat.GreenMask | PictFormat.BlueMask |
                 PictFormat.Alpha | PictFormat.AlphaMask)
    },

    # A_1
    {
        'template': {
            'id': 0,
            'type': render.PictType.Direct,
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

        'mask': (PictFormat.Type | PictFormat.Depth | PictFormat.RedMask |
                 PictFormat.GreenMask | PictFormat.BlueMask |
                 PictFormat.Alpha | PictFormat.AlphaMask)
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
        if mask & PictFormat.Id:
            if template['id'] != format.id:
                continue
        if mask & PictFormat.Type:
            if template['type'] != format.type:
                continue
        if mask & PictFormat.Depth:
            if template['depth'] != format.depth:
                continue
        if mask & PictFormat.Red:
            if template['direct']['red'] != format.direct.red_shift:
                continue
        if mask & PictFormat.RedMask:
            if template['direct']['red_mask'] != format.direct.red_mask:
                continue
        if mask & PictFormat.Green:
            if template['direct']['green'] != format.direct.green_shift:
                continue
        if mask & PictFormat.GreenMask:
            if template['direct']['green_mask'] != format.direct.green_mask:
                continue
        if mask & PictFormat.Blue:
            if template['direct']['blue'] != format.direct.blue_shift:
                continue
        if mask & PictFormat.BlueMask:
            if template['direct']['blue_mask'] != format.direct.blue_mask:
                continue
        if mask & PictFormat.Alpha:
            if template['direct']['alpha'] != format.direct.alpha_shift:
                continue
        if mask & PictFormat.AlphaMask:
            if template['direct']['alpha_mask'] != format.direct.alpha_mask:
                continue
        if mask & PictFormat.Colormap:
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

