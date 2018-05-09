"""
A set of functions to faciliate binding to mouse button presses.

This is basically the companion module of 'keybind.py'. The good news is that
we don't have to deal with the complexity of X's keysym table. The bad news is
that mice binding and dragging comes with its own hairball of complexity.

TODO: Mouse bindings that hook into the event dipatcher like the keybind
      module. Also, functions that abstract the process of using the mouse
      to drag something.
"""
from collections import defaultdict

from xpybutil.compat import xproto

from xpybutil import conn, root

__mousebinds = defaultdict(list)
__mousegrabs = defaultdict(int) # Mouse grab key -> number of grabs

EM = xproto.EventMask
GM = xproto.GrabMode
TRIVIAL_MODS = [
    0,
    xproto.ModMask.Lock,
    xproto.ModMask._2,
    xproto.ModMask.Lock | xproto.ModMask._2
]

def parse_buttonstring(button_string):
    """
    A utility function to turn strings like 'Mod1-Shift-3' into a pair
    corresponding to its modifiers and button number.

    :param button_string: String starting with zero or more modifiers followed
                          by exactly one button number.

                          Available modifiers: Control, Mod1, Mod2, Mod3, Mod4,
                          Mod5, Shift, Lock
    :type button_string: str
    :return: Tuple of modifier mask and button number
    :rtype: (mask, int)
    """
    mods, button = 0, None
    for part in button_string.split('-'):
        if hasattr(xproto.KeyButMask, part):
            mods |= getattr(xproto.KeyButMask, part)
        else:
            button = int(part)

    return mods, button

def grab_pointer(grab_win, confine, cursor):
    """
    This will grab the pointer. The effect is that further pointer events will
    *only* be sent to the grabbing client (i.e., ``grab_win``).

    :param grab_win: A window identifier to report pointer events to.
    :type grab_win: int
    :param confine: Either a window identifier to confine the pointer to, or
                    None if no confinement is desired.
    :type confine: int
    :param cursor: A cursor identifier. (See the ``cursor`` module.)
    :rtype: xcb.xproto.GrabStatus
    """
    mask = EM.PointerMotion | EM.ButtonRelease | EM.ButtonPress
    return conn.core.GrabPointer(False, grab_win, mask, GM.Async, GM.Async,
                                 confine, cursor,
                                 xproto.Time.CurrentTime).reply()

def ungrab_pointer():
    """
    This will release a grab initiated by ``grab_pointer``.

    :rtype: void
    """
    conn.core.UngrabPointerChecked(xproto.Time.CurrentTime).check()

def grab_button(wid, modifiers, button, propagate=False):
    """
    Grabs a mouse button for a particular window and a modifiers/key value.
    If the grab was successful, return True. Otherwise, return False.
    If your client is grabbing buttons, it is useful to notify the user if a
    button wasn't grabbed. Mouse shortcuts not responding is disorienting!

    Also, this function will grab several buttons based on varying modifiers.
    Namely, this accounts for all of the "trivial" modifiers that may have
    an effect on X events, but probably shouldn't effect button grabbing. (i.e.,
    whether num lock or caps lock is on.)

    If 'propagate' is True, then no further events can be processed until the
    grabbing client allows them to be. (Which is done via AllowEvents. Thus,
    if propagate is True, you *must* make some call to AllowEvents at some
    point, or else your client will lock.)

    N.B. You should probably be using 'bind_mouse' or 'bind_global_mouse'
    instead.

    :param wid: A window identifier.
    :type wid: int
    :param modifiers: A modifier mask.
    :type modifiers: int
    :param button: A button number.
    :type button: int
    :param propagate: Whether to grab synchronously (True) or
                      asynchronously (False). When in doubt, keep it set
                      to False.
    :type propagate: bool
    :rtype: bool
    """
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
    """
    Ungrabs a button that was grabbed by ``grab_button``. Similarly, it
    will return True on success and False on failure.

    When ungrabbing a button, the parameters to this function should be
    *precisely* the same as the parameters to ``grab_button``.

    :param wid: A window identifier.
    :type wid: int
    :param modifiers: A modifier mask.
    :type modifiers: int
    :param button: A button number.
    :type button: int
    :rtype: bool
    """
    try:
        for mod in TRIVIAL_MODS:
            conn.core.UngrabButtonChecked(button, wid, modifiers | mod).check()

        return True
    except xproto.BadAccess:
        return False

def bind_global_mouse(event_type, key_string, cb):
    """
    An alias for ``bind_mouse(event_type, ROOT_WINDOW, key_string, cb)``.

    :param event_type: Either 'ButtonPress' or 'ButtonRelease'.
    :type event_type: str
    :param key_string: A string of the form 'Mod1-Control-3'.
                       Namely, a list of zero or more modifiers separated by
                       '-', followed by a single button digit.
    :type key_string: str
    :param cb: A first class function with no parameters.
    :type cb: function
    :return: True if the binding was successful, False otherwise.
    :rtype: bool
    """
    return bind_mouse(event_type, root, key_string, cb)

def bind_mouse(event_type, wid, button_string, cb):
    raise NotImplemented

