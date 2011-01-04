import struct

import xcb.xproto

import util

__atoms = ['WM_PROTOCOLS', 'WM_TAKE_FOCUS', 'WM_SAVE_YOURSELF',
           'WM_DELETE_WINDOW', 'WM_COLORMAP_WINDOWS', 'WM_STATE']

class Hint:
    Input = 1
    State = 2
    IconPixmap = 4
    IconWindow = 8
    IconPosition = 16
    IconMask = 32
    WindowGroup = 64
    Message = 128
    Urgency = 256

class SizeHint:
    USPosition = 1
    USSize = 2
    PPosition = 4
    PSize = 8
    PMinSize = 16
    PMaxSize = 32
    PResizeInc = 64
    PAspect = 128
    PBaseSize = 256
    PWinGravity = 512

class State:
    Withdrawn = 0
    Normal = 1
    Zoomed = 2
    Iconic = 3
    Inactive = 4

# Handle atom caching
def build_atom_cache(c):
    for atom in __atoms:
        util.__atom_cache[atom] = util.get_atom_cookie(c, atom,
                                                       only_if_exists=False)

# WM_NAME

def get_wm_name(c, window):
    return util.PropertyCookie(
        util.get_property(c, window, xcb.xproto.Atom.WM_NAME))

def get_wm_name_unchecked(c, window):
    return util.PropertyCookie(
        util.get_property_unchecked(c, window, xcb.xproto.Atom.WM_NAME))

def set_wm_name(c, window, wm_name):
    return c.core.ChangeProperty(xcb.xproto.PropMode.Replace, window,
                                    xcb.xproto.Atom.WM_NAME,
                                    xcb.xproto.Atom.STRING, 8, len(wm_name),
                                    wm_name)

def set_wm_name_checked(c, window, wm_name):
    return c.core.ChangePropertyChecked(xcb.xproto.PropMode.Replace, window,
                                    xcb.xproto.Atom.WM_NAME,
                                    xcb.xproto.Atom.STRING, 8, len(wm_name),
                                    wm_name)

# WM_ICON_NAME

def get_wm_icon_name(c, window):
    return util.PropertyCookie(
        util.get_property(c, window, xcb.xproto.Atom.WM_ICON_NAME))

def get_wm_icon_name_unchecked(c, window):
    return util.PropertyCookie(
        util.get_property_unchecked(c, window, xcb.xproto.Atom.WM_ICON_NAME))

def set_wm_icon_name(c, window, wm_icon_name):
    return c.core.ChangeProperty(xcb.xproto.PropMode.Replace, window,
                                    xcb.xproto.Atom.WM_ICON_NAME,
                                    xcb.xproto.Atom.STRING, 8,
                                    len(wm_icon_name), wm_icon_name)

def set_wm_icon_name_checked(c, window, wm_icon_name):
    return c.core.ChangePropertyChecked(xcb.xproto.PropMode.Replace, window,
                                    xcb.xproto.Atom.WM_ICON_NAME,
                                    xcb.xproto.Atom.STRING, 8,
                                    len(wm_icon_name), wm_icon_name)

# WM_NORMAL_HINTS

class NormalHintsCookie(util.PropertyCookie):
    def reply(self):
        v = util.PropertyCookie.reply(self)

        if not v:
            return None

        return {
            'flags': {
                'USPosition': v[0] & SizeHint.USPosition > 0,
                'USSize': v[0] & SizeHint.USSize > 0,
                'PPosition': v[0] & SizeHint.PPosition > 0,
                'PSize': v[0] & SizeHint.PSize > 0,
                'PMinSize': v[0] & SizeHint.PMinSize > 0,
                'PMaxSize': v[0] & SizeHint.PMaxSize > 0,
                'PResizeInc': v[0] & SizeHint.PResizeInc > 0,
                'PAspect': v[0] & SizeHint.PAspect > 0,
                'PBaseSize': v[0] & SizeHint.PBaseSize > 0,
                'PWinGravity': v[0] & SizeHint.PWinGravity > 0
            },
            'x': v[1],
            'y': v[2],
            'width': v[3],
            'height': v[4],
            'min_width': v[5],
            'min_height': v[6],
            'max_width': v[7],
            'max_height': v[8],
            'width_inc': v[9],
            'height_inc': v[10],
            'min_aspect_num': v[11],
            'min_aspect_den': v[12],
            'max_aspect_num': v[13],
            'max_aspect_den': v[14],
            'base_width': v[15],
            'base_height': v[16],
            'win_gravity': v[17] if v[17] > 0 else xcb.xproto.Gravity.NorthWest
        }

def get_wm_normal_hints(c, window):
    return NormalHintsCookie(
        util.get_property(c, window, xcb.xproto.Atom.WM_NORMAL_HINTS))

def get_wm_normal_hints_unchecked(c, window):
    return NormalHintsCookie(
        util.get_property(c, window, xcb.xproto.Atom.WM_NORMAL_HINTS))

def _pack_normal_hints(flags, x, y, width, height, min_width, min_height,
                       max_width, max_height, width_inc, height_inc,
                       min_aspect_num, min_aspect_den, max_aspect_num,
                       max_aspect_den, base_width, base_height, win_gravity):
    hints = [0] * 18

    if flags & SizeHint.USPosition:
        hints[1], hints[2] = x, y
    elif flags & SizeHint.PPosition:
        hints[1], hints[2] = x, y

    if flags & SizeHint.USSize:
        hints[3], hints[4] = width, height
    elif flags & SizeHint.PSize:
        hints[3], hints[4] = width, height

    if flags & SizeHint.PMinSize:
        hints[5], hints[6] = min_width, min_height

    if flags & SizeHint.PMaxSize:
        hints[7], hints[8] = max_width, max_height

    if flags & SizeHint.PResizeInc:
        hints[9], hints[10] = width_inc, height_inc

    if flags & SizeHint.PAspect:
        hints[11], hints[12] = min_aspect_num, min_aspect_den
        hints[13], hints[14] = max_aspect_num, max_aspect_den

    if flags & SizeHint.PBaseSize:
        hints[15], hints[16] = base_width, base_height

    if flags & SizeHint.PWinGravity:
        hints[17] = win_gravity

    hints[0] = flags

    return struct.pack('I' * 18, *hints)

def set_wm_normal_hints(c, window, flags, x=0, y=0, width=0,
                        height=0, min_width=0, min_height=0,
                        max_width=0, max_height=0, width_inc=0,
                        height_inc=0, min_aspect_num=0,
                        min_aspect_den=0, max_aspect_num=0,
                        max_aspect_den=0, base_width=0, base_height=0,
                        win_gravity=xcb.xproto.Gravity.NorthWest):
    packed = _pack_normal_hints(flags, x, y, width, height, min_width,
                                min_height, max_width, max_height, width_inc,
                                height_inc, min_aspect_num, min_aspect_den,
                                max_aspect_num, max_aspect_den, base_width,
                                base_height, win_gravity)
    return c.core.ChangeProperty(xcb.xproto.PropMode.Replace, window,
                                    xcb.xproto.Atom.WM_NORMAL_HINTS,
                                    xcb.xproto.Atom.WM_SIZE_HINTS, 32,
                                    18, packed)

def set_wm_normal_hints_checked(c, window, flags, x=0, y=0, width=0,
                                height=0, min_width=0, min_height=0,
                                max_width=0, max_height=0, width_inc=0,
                                height_inc=0, min_aspect_num=0,
                                min_aspect_den=0, max_aspect_num=0,
                                max_aspect_den=0, base_width=0, base_height=0,
                                win_gravity=xcb.xproto.Gravity.NorthWest):
    packed = _pack_normal_hints(flags, x, y, width, height, min_width,
                                min_height, max_width, max_height, width_inc,
                                height_inc, min_aspect_num, min_aspect_den,
                                max_aspect_num, max_aspect_den, base_width,
                                base_height, win_gravity)
    return c.core.ChangePropertyChecked(xcb.xproto.PropMode.Replace, window,
                                    xcb.xproto.Atom.WM_NORMAL_HINTS,
                                    xcb.xproto.Atom.WM_SIZE_HINTS, 32,
                                    18, packed)

# WM_HINTS

class HintsCookie(util.PropertyCookie):
    def reply(self):
        v = util.PropertyCookie.reply(self)

        if not v:
            return None

        return {
            'flags': {
                'Input': v[0] & Hint.Input > 0,
                'State': v[0] & Hint.State > 0,
                'IconPixmap': v[0] & Hint.IconPixmap > 0,
                'IconWindow': v[0] & Hint.IconWindow > 0,
                'IconPosition': v[0] & Hint.IconPosition > 0,
                'IconMask': v[0] & Hint.IconMask > 0,
                'WindowGroup': v[0] & Hint.WindowGroup > 0,
                'Message': v[0] & Hint.Message > 0,
                'Urgency': v[0] & Hint.Urgency > 0
            },
            'input': v[1],
            'initial_state': v[2],
            'icon_pixmap': v[3],
            'icon_window': v[4],
            'icon_x': v[5],
            'icon_y': v[6],
            'icon_mask': v[7],
            'window_group': v[8],
        }

def get_wm_hints(c, window):
    return HintsCookie(
        util.get_property(c, window, xcb.xproto.Atom.WM_HINTS))

def get_wm_hints_unchecked(c, window):
    return HintsCookie(
        util.get_property_unchecked(c, window, xcb.xproto.Atom.WM_HINTS))

def _pack_hints(flags, input, initial_state, icon_pixmap, icon_window,
                icon_x, icon_y, icon_mask, window_group):
    hints = [0] * 9

    if flags & Hint.Input:
        hints[1] = input

    if flags & Hint.State:
        hints[2] = initial_state

    if flags & Hint.IconPixmap:
        hints[3] = icon_pixmap

    if flags & Hint.IconWindow:
        hints[4] = icon_window

    if flags & Hint.IconPosition:
        hints[5], hints[6] = icon_x, icon_y

    if flags & Hint.IconMask:
        hints[7] = icon_mask

    if flags & Hint.WindowGroup:
        hints[8] = window_group

    hints[0] = flags

    return struct.pack('I' * 9, *hints)

def set_wm_hints(c, window, flags, input=1, initial_state=State.Normal,
                 icon_pixmap=0, icon_window=0, icon_x=0, icon_y=0,
                 icon_mask=0, window_group=0):
    packed = _pack_hints(flags, input, initial_state, icon_pixmap, icon_window,
                         icon_x, icon_y, icon_mask, window_group)
    return c.core.ChangeProperty(xcb.xproto.PropMode.Replace, window,
                                    xcb.xproto.Atom.WM_HINTS,
                                    xcb.xproto.Atom.WM_HINTS, 32,
                                    9, packed)

def set_wm_hints_checked(c, window, flags, input=1,
                         initial_state=State.Normal, icon_pixmap=0,
                         icon_window=0, icon_x=0, icon_y=0, icon_mask=0,
                         window_group=0):
    packed = _pack_hints(flags, input, initial_state, icon_pixmap, icon_window,
                         icon_x, icon_y, icon_mask, window_group)
    return c.core.ChangePropertyChecked(xcb.xproto.PropMode.Replace, window,
                                    xcb.xproto.Atom.WM_HINTS,
                                    xcb.xproto.Atom.WM_HINTS, 32,
                                    9, packed)

# WM_CLASS

def get_wm_class(c, window):
    return util.PropertyCookie(
        util.get_property(c, window, xcb.xproto.Atom.WM_CLASS))

def get_wm_class_unchecked(c, window):
    return util.PropertyCookie(
        util.get_property_unchecked(c, window, xcb.xproto.Atom.WM_CLASS))

def set_wm_class(c, window, instance, cls):
    return c.core.ChangeProperty(xcb.xproto.PropMode.Replace, window,
                                    xcb.xproto.Atom.WM_CLASS,
                                    xcb.xproto.Atom.STRING, 8,
                                    len(instance) + len(cls) + 2,
                                    instance + chr(0) + cls + chr(0))

def set_wm_class_checked(c, window, instance, cls):
    return c.core.ChangePropertyChecked(xcb.xproto.PropMode.Replace, window,
                                    xcb.xproto.Atom.WM_CLASS,
                                    xcb.xproto.Atom.STRING, 8,
                                    len(instance) + len(cls) + 2,
                                    instance + chr(0) + cls + chr(0))

# WM_TRANSIENT_FOR

def get_wm_transient_for(c, window):
    return util.PropertyCookie(
        util.get_property(c, window, xcb.xproto.Atom.WM_TRANSIENT_FOR))

def get_wm_transient_for_unchecked(c, window):
    return util.PropertyCookie(
        util.get_property_unchecked(c, window,
                                    xcb.xproto.Atom.WM_TRANSIENT_FOR))

def set_wm_transient_for(c, window, transient_window):
    packed = struct.pack('I', transient_window)
    return c.core.ChangeProperty(xcb.xproto.PropMode.Replace, window,
                                    xcb.xproto.Atom.WM_TRANSIENT_FOR,
                                    xcb.xproto.Atom.WINDOW, 32,
                                    1, packed)

def set_wm_transient_for_checked(c, window, transient_window):
    packed = struct.pack('I', transient_window)
    return c.core.ChangePropertyChecked(xcb.xproto.PropMode.Replace, window,
                                    xcb.xproto.Atom.WM_TRANSIENT_FOR,
                                    xcb.xproto.Atom.WINDOW, 32,
                                    1, packed)

# WM_PROTOCOLS

def get_wm_protocols(c, window):
    return util.PropertyCookie(
        util.get_property(c, window, util.get_atom(c, 'WM_PROTOCOLS')))

def get_wm_protocols(c, window):
    return util.PropertyCookie(
        util.get_property_unchecked(c, window,
                                    util.get_atom(c, 'WM_PROTOCOLS')))

def set_wm_protocols(c, window, protocol_atoms):
    packed = struct.pack('I', transient_window)
    return c.core.ChangeProperty(xcb.xproto.PropMode.Replace, window,
                                    xcb.xproto.Atom.WM_TRANSIENT_FOR,
                                    xcb.xproto.Atom.WINDOW, 32,
                                    1, packed)

def set_wm_protocols_checked(c, window, protocol_atoms):
    packed = struct.pack('I' * len(protocol_atoms), *protocol_atoms)
    return c.core.ChangePropertyChecked(xcb.xproto.PropMode.Replace, window,
                                    util.get_atom(c, 'WM_PROTOCOLS'),
                                    xcb.xproto.Atom.ATOM, 32,
                                    len(protocol_atoms), packed)

# WM_COLORMAP_WINDOWS

def get_wm_colormap_windows(c, window):
    return util.PropertyCookie(
        util.get_property(c, window, util.get_atom(c, 'WM_COLORMAP_WINDOWS')))

def get_wm_colormap_windows_unchecked(c, window):
    return util.PropertyCookie(
        util.get_property_unchecked(c, window,
                                    util.get_atom(c, 'WM_COLORMAP_WINDOWS')))

def set_wm_colormap_windows(c, window, colormap_windows):
    packed = struct.pack('I' * len(colormap_windows), *colormap_windows)
    return c.core.ChangeProperty(xcb.xproto.PropMode.Replace, window,
                                    util.get_atom(c, 'WM_COLORMAP_WINDOWS'),
                                    xcb.xproto.Atom.WINDOW, 32,
                                    len(colormap_windows), packed)

def set_wm_colormap_windows_checked(c, window, transient_window):
    packed = struct.pack('I' * len(colormap_windows), *colormap_windows)
    return c.core.ChangePropertyChecked(xcb.xproto.PropMode.Replace, window,
                                    util.get_atom(c, 'WM_COLORMAP_WINDOWS'),
                                    xcb.xproto.Atom.WINDOW, 32,
                                    len(colormap_windows), packed)

# WM_CLIENT_MACHINE

def get_wm_client_machine(c, window):
    return util.PropertyCookie(
        util.get_property(c, window, xcb.xproto.Atom.WM_CLIENT_MACHINE))

def get_wm_client_machine_unchecked(c, window):
    return util.PropertyCookie(
        util.get_property_unchecked(c, window,
                                    xcb.xproto.Atom.WM_CLIENT_MACHINE))

def set_wm_client_machine(c, window, client_machine):
    return c.core.ChangeProperty(xcb.xproto.PropMode.Replace, window,
                                    xcb.xproto.Atom.WM_CLIENT_MACHINE,
                                    xcb.xproto.Atom.STRING, 8,
                                    len(client_machine), client_machine)

def set_wm_client_machine_checked(c, window, client_machine):
    return c.core.ChangePropertyChecked(xcb.xproto.PropMode.Replace, window,
                                    xcb.xproto.Atom.WM_CLIENT_MACHINE,
                                    xcb.xproto.Atom.STRING, 8,
                                    len(client_machine), client_machine)

# WM_STATE

class StateCookie(util.PropertyCookie):
    def reply(self):
        v = util.PropertyCookie.reply(self)

        if not v:
            return None

        return {
            'state': v[0],
            'icon': v[1]
        }

def get_wm_state(c, window):
    return StateCookie(
        util.get_property(c, window, util.get_atom(c, 'WM_STATE')))

def get_wm_state_unchecked(c, window):
    return StateCookie(
        util.get_property_unchecked(c, window, util.get_atom(c, 'WM_STATE')))

def set_wm_state(c, window, state, icon):
    packed = struct.pack('II', state, icon)
    return c.core.ChangeProperty(xcb.xproto.PropMode.Replace, window,
                                    util.get_atom(c, 'WM_STATE'),
                                    util.get_atom(c, 'WM_STATE'), 32,
                                    2, packed)

def set_wm_state_checked(c, window, state, icon):
    packed = struct.pack('II', state, icon)
    return c.core.ChangePropertyChecked(xcb.xproto.PropMode.Replace, window,
                                    util.get_atom(c, 'WM_STATE'),
                                    util.get_atom(c, 'WM_STATE'), 32,
                                    2, packed)

# WM_ICON_SIZE

class IconSizeCookie(util.PropertyCookie):
    def reply(self):
        v = util.PropertyCookie.reply(self)

        if not v:
            return None

        return {
            'min_width': v[0],
            'min_height': v[1],
            'max_width': v[2],
            'max_height': v[3],
            'width_inc': v[4],
            'height_inc': v[5]
        }

def get_icon_size(c, window):
    return IconSizeCookie(
        util.get_property(c, window, xcb.xproto.Atom.WM_ICON_SIZE))

def get_icon_size_unchecked(c, window):
    return IconSizeCookie(
        util.get_property_unchecked(c, window, xcb.xproto.Atom.WM_ICON_SIZE))

def set_icon_size(c, window, min_width=0, min_height=0, max_width=0,
                 max_height=0, width_inc=0, height_inc=0):
    packed = struct.pack('I' * 6, min_width, min_height, max_width, max_height,
                                  width_inc, height_inc)
    return c.core.ChangeProperty(xcb.xproto.PropMode.Replace, window,
                                    xcb.xproto.Atom.WM_ICON_SIZE,
                                    xcb.xproto.Atom.WM_ICON_SIZE, 32,
                                    6, packed)

def set_icon_size_checked(c, window, min_width=0, min_height=0, max_width=0,
                         max_height=0, width_inc=0, height_inc=0):
    packed = struct.pack('I' * 6, min_width, min_height, max_width, max_height,
                                  width_inc, height_inc)
    return c.core.ChangePropertyChecked(xcb.xproto.PropMode.Replace, window,
                                    xcb.xproto.Atom.WM_ICON_SIZE,
                                    xcb.xproto.Atom.WM_ICON_SIZE, 32,
                                    6, packed)
