import xcb.xproto

from keysymdef import keysyms, keycodes

TRIVIAL_MODS = [
    0,
    xcb.xproto.ModMask.Lock,
    xcb.xproto.ModMask._2,
    xcb.xproto.ModMask.Lock | xcb.xproto.ModMask._2
]

def _get_min_max_keycode(c):
    return c.get_setup().min_keycode, c.get_setup().max_keycode

def get_keyboard_mapping(c):
    mn, mx = _get_min_max_keycode(c)

    return c.core.GetKeyboardMapping(mn, mx - mn + 1)

def get_keyboard_mapping_unchecked(c):
    mn, mx = _get_min_max_keycode(c)

    return c.core.GetKeyboardMappingUnchecked(mn, mx - mn + 1)

def get_keysym(c, syms, keycode, col=0):
    assert isinstance(syms, xcb.xproto.GetKeyboardMappingReply)

    mn, mx = _get_min_max_keycode(c)
    per = syms.keysyms_per_keycode

    return syms.keysyms[(keycode - mn) * per]

def get_keycode(c, syms, keysym):
    assert isinstance(syms, xcb.xproto.GetKeyboardMappingReply)

    res = []
    mn, mx = _get_min_max_keycode(c)
    for j in xrange(mn, mx + 1):
        ks = get_keysym(c, syms, j)
        if ks == keysym:
            return j

    return None

def get_modifiers(state):
    ret = []

    if state & xcb.xproto.ModMask.Shift:
        ret.append('Shift')
    if state & xcb.xproto.ModMask.Lock:
        ret.append('Lock')
    if state & xcb.xproto.ModMask.Control:
        ret.append('Control')
    if state & xcb.xproto.ModMask._1:
        ret.append('Mod1')
    if state & xcb.xproto.ModMask._2:
        ret.append('Mod2')
    if state & xcb.xproto.ModMask._3:
        ret.append('Mod3')
    if state & xcb.xproto.ModMask._4:
        ret.append('Mod4')
    if state & xcb.xproto.ModMask._5:
        ret.append('Mod5')
    if state & xcb.xproto.KeyButMask.Button1:
        ret.append('Button1')
    if state & xcb.xproto.KeyButMask.Button2:
        ret.append('Button2')
    if state & xcb.xproto.KeyButMask.Button3:
        ret.append('Button3')
    if state & xcb.xproto.KeyButMask.Button4:
        ret.append('Button4')
    if state & xcb.xproto.KeyButMask.Button5:
        ret.append('Button5')

    return ret

def grab_pointer(c, grab_win, confine, cursor):
    c.core.GrabPointer(
            False, grab_win,
            xcb.xproto.EventMask.PointerMotion |
            xcb.xproto.EventMask.ButtonRelease |
            xcb.xproto.EventMask.ButtonPress,
            xcb.xproto.GrabMode.Async, xcb.xproto.GrabMode.Async,
            confine, cursor, xcb.xproto.Time.CurrentTime
        )

def ungrab_pointer(c):
    c.core.UngrabPointer(xcb.xproto.Time.CurrentTime)

def grab_keyboard(c, grab_win):
    c.core.GrabKeyboard(
        False, grab_win, xcb.xproto.Time.CurrentTime,
        xcb.xproto.GrabMode.Async, xcb.xproto.GrabMode.Async
    )

def ungrab_keyboard(c):
    c.core.UngrabKeyboard(xcb.xproto.Time.CurrentTime)

def grab_key(c, wid, modifiers, key):
    try:
        for mod in TRIVIAL_MODS:
            c.core.GrabKeyChecked(True, wid, modifiers | mod, key,
                                  xcb.xproto.GrabMode.Async,
                                  xcb.xproto.GrabMode.Async).check()

        return True
    except xcb.xproto.BadAccess:
        return False

def ungrab_key(c, wid, modifiers, key):
    try:
        for mod in TRIVIAL_MODS:
            c.core.UngrabKeyChecked(key, wid, modifiers | mod).check()

        return True
    except xcb.xproto.BadAccess:
        return False

def grab_button(c, wid, modifiers, button, propagate=False):
    emask = (xcb.xproto.EventMask.ButtonPress |
             xcb.xproto.EventMask.ButtonRelease |
             xcb.xproto.EventMask.ButtonMotion)
    mode = xcb.xproto.GrabMode.Sync if propagate else xcb.xproto.GrabMode.Async

    try:
        for mod in TRIVIAL_MODS:
            c.core.GrabButtonChecked(True, wid, emask,
                                     mode,
                                     xcb.xproto.GrabMode.Async, 0, 0,
                                     button, modifiers | mod).check()

        return True
    except xcb.xproto.BadAccess:
        return False

def ungrab_button(c, wid, modifiers, button):
    try:
        for mod in TRIVIAL_MODS:
            c.core.UngrabButtonChecked(button, wid, modifiers | mod).check()

        return True
    except xcb.xproto.BadAccess:
        return False

def lookup_string(c, syms, kstr):
    assert isinstance(syms, xcb.xproto.GetKeyboardMappingReply)

    if kstr in keysyms:
        return get_keycode(c, syms, keysyms[kstr])
    elif len(kstr) > 1 and kstr.capitalize() in keysyms:
        return get_keycode(c, syms, keysyms[kstr.capitalize()])

    return None

def lookup_keysym(keysym):
    if keysym in keycodes:
        return keycodes[keysym][0]
    return None
