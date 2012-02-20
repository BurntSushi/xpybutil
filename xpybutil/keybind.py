"""
A set of functions devoted to binding key presses and registering
callbacks. This will automatically hook into the event callbacks
in event.py.
"""
from collections import defaultdict
import sys

import xcb.xproto as xproto

from xpybutil import conn, root
import event
from keysymdef import keysyms, keysym_strings

__kbmap = None
__keysmods = None

__keybinds = defaultdict(list)
__mousebinds = defaultdict(list)

__keygrabs = defaultdict(int) # Key grab key -> number of grabs
__mousegrabs = defaultdict(int)

EM = xproto.EventMask
GM = xproto.GrabMode
TRIVIAL_MODS = [
    0,
    xproto.ModMask.Lock,
    xproto.ModMask._2,
    xproto.ModMask.Lock | xproto.ModMask._2
]

def parse_keystring(key_string):
    """
    A utility function to turn strings like 'Mod1-Mod4-a' into a pair
    corresponding to its modifiers and keycode.
    """
    modifiers = 0
    keycode = None

    for part in key_string.split('-'):
        if hasattr(xproto.KeyButMask, part):
            modifiers |= getattr(xproto.KeyButMask, part)
        else:
            if len(part) == 1:
                part = part.lower()
            keycode = lookup_string(part)

    return modifiers, keycode

def parse_buttonstring(button_string):
    mods, button = 0, None
    for part in button_string.split('-'):
        if hasattr(xproto.KeyButMask, part):
            mods |= getattr(xproto.KeyButMask, part)
        else:
            button = int(part)

    return mods, button

def lookup_string(kstr):
    if kstr in keysyms:
        return get_keycode(keysyms[kstr])
    elif len(kstr) > 1 and kstr.capitalize() in keysyms:
        return get_keycode(keysyms[kstr.capitalize()])

    return None

def lookup_keysym(keysym):
    if keysym in keysym_strings:
        return keysym_strings[keysym][0]
    return None

def get_min_max_keycode():
    return conn.get_setup().min_keycode, conn.get_setup().max_keycode

def get_keyboard_mapping():
    mn, mx = get_min_max_keycode()

    return conn.core.GetKeyboardMapping(mn, mx - mn + 1)

def get_keyboard_mapping_unchecked():
    mn, mx = get_min_max_keycode()

    return conn.core.GetKeyboardMappingUnchecked(mn, mx - mn + 1)

def get_keysym(keycode, col=0, kbmap=None):
    if kbmap is None:
        kbmap = __kbmap

    mn, mx = get_min_max_keycode()
    per = kbmap.keysyms_per_keycode
    ind = (keycode - mn) * per + col

    return __kbmap.keysyms[ind]

def get_keysym_string(keysym):
    return keysym_strings[keysym][0]

def get_keycode(keysym):
    mn, mx = get_min_max_keycode()
    cols = __kbmap.keysyms_per_keycode
    for i in xrange(mn, mx + 1):
        for j in xrange(0, cols):
            ks = get_keysym(i, col=j)
            if ks == keysym:
                return i

    return None

def get_mod_for_key(keycode):
    return __keysmods.get(keycode, 0)

def get_keys_to_mods():
    mm = xproto.ModMask
    modmasks = [mm.Shift, mm.Lock, mm.Control,
                mm._1, mm._2, mm._3, mm._4, mm._5] # order matters

    mods = conn.core.GetModifierMapping().reply()

    res = {}
    keyspermod = mods.keycodes_per_modifier
    for mmi in xrange(0, len(modmasks)):
        row = mmi * keyspermod
        for kc in mods.keycodes[row:row + keyspermod]:
            res[kc] = modmasks[mmi]

    return res

def get_modifiers(state):
    ret = []

    if state & xproto.ModMask.Shift:
        ret.append('Shift')
    if state & xproto.ModMask.Lock:
        ret.append('Lock')
    if state & xproto.ModMask.Control:
        ret.append('Control')
    if state & xproto.ModMask._1:
        ret.append('Mod1')
    if state & xproto.ModMask._2:
        ret.append('Mod2')
    if state & xproto.ModMask._3:
        ret.append('Mod3')
    if state & xproto.ModMask._4:
        ret.append('Mod4')
    if state & xproto.ModMask._5:
        ret.append('Mod5')
    if state & xproto.KeyButMask.Button1:
        ret.append('Button1')
    if state & xproto.KeyButMask.Button2:
        ret.append('Button2')
    if state & xproto.KeyButMask.Button3:
        ret.append('Button3')
    if state & xproto.KeyButMask.Button4:
        ret.append('Button4')
    if state & xproto.KeyButMask.Button5:
        ret.append('Button5')

    return ret

def grab_pointer(grab_win, confine, cursor):
    mask = EM.PointerMotion | EM.ButtonRelease | EM.ButtonPress
    conn.core.GrabPointer(False, grab_win, mask, GM.Async, GM.Async,
                          confine, cursor, xproto.Time.CurrentTime)

def ungrab_pointer():
    conn.core.UngrabPointer(xproto.Time.CurrentTime)

def grab_keyboard(grab_win):
    return conn.core.GrabKeyboard(False, grab_win, xproto.Time.CurrentTime,
                                  GM.Async, GM.Async).reply()

def ungrab_keyboard():
    conn.core.UngrabKeyboardChecked(xproto.Time.CurrentTime).check()

def grab_key(wid, modifiers, key):
    try:
        for mod in TRIVIAL_MODS:
            conn.core.GrabKeyChecked(True, wid, modifiers | mod, key, GM.Async,
                                     GM.Async).check()

        return True
    except xproto.BadAccess:
        return False

def ungrab_key(wid, modifiers, key):
    try:
        for mod in TRIVIAL_MODS:
            conn.core.UngrabKeyChecked(key, wid, modifiers | mod).check()

        return True
    except xproto.BadAccess:
        return False

def grab_button(wid, modifiers, button, propagate=False):
    mask = EM.ButtonPress | EM.ButtonRelease | EM.ButtonMotion

    try:
        for mod in TRIVIAL_MODS:
            conn.core.GrabButtonChecked(True, wid, mask,
                                        GM.Sync if propagate else GM.Async,
                                        GM.Async, 0, 0,
                                        button, modifiers | mod).check()

        return True
    except xproto.BadAccess:
        return False

def ungrab_button(wid, modifiers, button):
    try:
        for mod in TRIVIAL_MODS:
            conn.core.UngrabButtonChecked(button, wid, modifiers | mod).check()

        return True
    except xproto.BadAccess:
        return False

def update_keyboard_mapping(e):
    global __kbmap, __keysmods

    newmap = get_keyboard_mapping().reply()

    if e is None:
        __kbmap = newmap
        __keysmods = get_keys_to_mods()
        return

    if e.request == xproto.Mapping.Keyboard:
        changes = {}
        for kc in xrange(*get_min_max_keycode()):
            knew = get_keysym(kc, kbmap=newmap)
            oldkc = get_keycode(knew)
            if oldkc != kc:
                changes[oldkc] = kc

        __kbmap = newmap
        __regrab(changes)
    elif e.request == xproto.Mapping.Modifier:
        __keysmods = get_keys_to_mods()

def __run_keybind_callbacks(e):
    kc, mods = e.detail, e.state
    for mod in TRIVIAL_MODS:
        mods &= ~mod

    key = (e.event, mods, kc)
    for cb in __keybinds.get(key, []):
        cb()

def __regrab(changes):
    for wid, mods, kc in __keybinds:
        if kc in changes:
            ungrab_key(wid, mods, kc)
            grab_key(wid, mods, changes[kc])

            old = (wid, mods, kc)
            new = (wid, mods, changes[kc])
            __keybinds[new] = __keybinds[old]
            del __keybinds[old]

    # XXX: todo mouse regrabbing

def bind_global_key(event_type, key_string, cb):
    return bind_key(event_type, root, key_string, cb)

def bind_key(event_type, wid, key_string, cb):
    assert event_type in ('KeyPress', 'KeyRelease')

    mods, kc = parse_keystring(key_string)
    key = (wid, mods, kc)

    if not kc:
        print >> sys.stderr, 'Could not find a keycode for %s' % key_string
        return False

    if not __keygrabs[key] and not grab_key(wid, mods, kc):
        return False

    __keybinds[key].append(cb)
    __keygrabs[key] += 1

    if not event.is_connected(event_type, wid, __run_keybind_callbacks):
        event.connect(event_type, wid, __run_keybind_callbacks)

    return True

def bind_mouse(event_type, wid, button_string, cb):
    raise NotImplemented

update_keyboard_mapping(None)
event.connect('MappingNotify', None, update_keyboard_mapping)

