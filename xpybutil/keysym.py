import xcb.xproto

from xpybutil import conn
from keysymdef import keysyms, keycodes

EM = xcb.xproto.EventMask
GM = GM
TRIVIAL_MODS = [
    0,
    xcb.xproto.ModMask.Lock,
    xcb.xproto.ModMask._2,
    xcb.xproto.ModMask.Lock | xcb.xproto.ModMask._2
]

def parse_keystring(key_string, kbmap):
    """
    A utility function to turn strings like 'Mod1-Mod4-a' into a pair
    corresponding to its modifiers and keycode.
    """
    modifiers = 0
    keycode = None

    for part in key_string.split('-'):
        if hasattr(xcb.xproto.KeyButMask, part):
            modifiers |= getattr(xcb.xproto.KeyButMask, part)
        else:
            if len(part) == 1:
                part = part.lower()
            keycode = lookup_string(kbmap, part)

    return modifiers, keycode

def parse_buttonstring(button_string):
    mods, button = 0, None
    for part in button_string.split('-'):
        if hasattr(xcb.xproto.KeyButMask, part):
            mods |= getattr(xcb.xproto.KeyButMask, part)
        else:
            button = int(part)

    return mods, button

def lookup_string(syms, kstr):
    assert isinstance(syms, xcb.xproto.GetKeyboardMappingReply)

    if kstr in keysyms:
        return get_keycode(syms, keysyms[kstr])
    elif len(kstr) > 1 and kstr.capitalize() in keysyms:
        return get_keycode(syms, keysyms[kstr.capitalize()])

    return None

def lookup_keysym(keysym):
    if keysym in keycodes:
        return keycodes[keysym][0]
    return None

def get_min_max_keycode():
    return conn.get_setup().min_keycode, conn.get_setup().max_keycode

def get_keyboard_mapping():
    mn, mx = get_min_max_keycode()

    return conn.core.GetKeyboardMapping(mn, mx - mn + 1)

def get_keyboard_mapping_unchecked(c):
    mn, mx = get_min_max_keycode()

    return conn.core.GetKeyboardMappingUnchecked(mn, mx - mn + 1)

def get_keysym(syms, keycode, col=0):
    assert isinstance(syms, xcb.xproto.GetKeyboardMappingReply)

    mn, mx = get_min_max_keycode()
    per = syms.keysyms_per_keycode
    ind = (keycode - mn) * per + col

    return syms.keysyms[ind]

def get_keysym_string(syms, keysym, col=0):
    assert isinstance(syms, xcb.xproto.GetKeyboardMappingReply)

    return keycodes[keysym][col]

def get_keycode(syms, keysym):
    assert isinstance(syms, xcb.xproto.GetKeyboardMappingReply)

    res = []
    mn, mx = get_min_max_keycode()
    cols = syms.keysyms_per_keycode
    for i in xrange(mn, mx + 1):
        for j in xrange(0, cols):
            ks = get_keysym(syms, i, col=j)
            if ks == keysym:
                return i

    return None

def get_keys_to_mods():
    mm = xcb.xproto.ModMask
    modmasks = [mm.Shift, mm.Lock, mm.Control,
                mm._1, mm._2, mm._3, mm._4, mm._5] # order matters

    mods = conn.core.GetModifierMapping().reply()

    res = {}
    keyspermod = mods.keycodes_per_modifier
    for mmi in xrange(0, len(modmasks)):
        row = mmi * keyspermod
        for kc in mods.keycodes[row:row + 4]:
            res[kc] = modmasks[mmi]

    return res

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

def grab_pointer(grab_win, confine, cursor):
    mask = EM.PointerMotion | EM.ButtonRelease | EM.ButtonPress
    conn.core.GrabPointer(False, grab_win, mask, GM.Async, GM.Async,
                          confine, cursor, xcb.xproto.Time.CurrentTime)

def ungrab_pointer():
    conn.core.UngrabPointer(xcb.xproto.Time.CurrentTime)

def grab_keyboard(grab_win):
    return conn.core.GrabKeyboard(False, grab_win, xcb.xproto.Time.CurrentTime,
                                  GM.Async, GM.Async).reply()

def ungrab_keyboard():
    conn.core.UngrabKeyboardChecked(xcb.xproto.Time.CurrentTime).check()

def grab_key(wid, modifiers, key):
    try:
        for mod in TRIVIAL_MODS:
            conn.core.GrabKeyChecked(True, wid, modifiers | mod, key, GM.Async,
                                     GM.Async).check()

        return True
    except xcb.xproto.BadAccess:
        return False

def ungrab_key(wid, modifiers, key):
    try:
        for mod in TRIVIAL_MODS:
            conn.core.UngrabKeyChecked(key, wid, modifiers | mod).check()

        return True
    except xcb.xproto.BadAccess:
        return False

def grab_button(wid, modifiers, button, propagate=False):
    mask = EM.ButtonPress | EM.ButtonRelease | EM.ButtonMotion

    try:
        for mod in TRIVIAL_MODS:
            c.core.GrabButtonChecked(True, wid, mask,
                                     GM.Sync if propagate else GM.Async,
                                     GM.Async, 0, 0,
                                     button, modifiers | mod).check()

        return True
    except xcb.xproto.BadAccess:
        return False

def ungrab_button(wid, modifiers, button):
    try:
        for mod in TRIVIAL_MODS:
            conn.core.UngrabButtonChecked(button, wid, modifiers | mod).check()

        return True
    except xcb.xproto.BadAccess:
        return False

