"""
A few utility functions related to client windows. In
particular, getting an accurate geometry of a client window
including the decorations (this can vary with the window
manager). Also, a functon to move and/or resize a window
accurately by the top-left corner. (Also can change based on
the currently running window manager.)

This module also contains a function 'listen' that must be used
in order to receive certain events from a window. For example,
if you wanted to run 'func' whenever a property on the root
window changed, you could do something like:

  ::

    import xpybutil
    import xpybutil.event as event
    import xpybutil.ewmh as ewmh
    import xpybutil.util as util
    import xpybutil.window as window

    def func(e):
      if util.get_atom_name(e.atom) == '_NET_ACTIVE_WINDOW':
        # Do something whenever the active window changes
        active_window_id = ewmh.get_active_window().reply()

    window.listen(xpybutil.root, 'PropertyChange')
    event.connect('PropertyNotify', xpybutil.root, func)

The idea here is to tell X that you want events that fall under
the 'PropertyChange' category. Then you bind 'func' to the
particular event 'PropertyNotify'.
"""
from xpybutil.compat import xproto

from xpybutil import conn
import xpybutil.ewmh as ewmh

class WindowManagers(object):
    """
    A list of window managers that xpybutil is aware of.

    These mostly modify how we determine the size of a client. In particular,
    KWin's decorations are in the parent of the parent of the client, whereas
    in Openbox, they are simply in the parent of the client.

    I am not sure whether I have plans to expand this list.
    """
    Unknown = 0
    Openbox = 1
    KWin = 2

def listen(window, *event_mask_names):
    """
    Makes X report events for the masks provided.

    This function must be called in order to get X send you events about a
    particular window. (i.e., it is not simply enough to call 'event.connect'.)

    This page is required reading if you are to do any event processing:
    http://tronche.com/gui/x/xlib/events/processing-overview.html

    :param window: Window identifier.
    :type window: int
    :param event_mask_names: List of mask names.
    :type event_mask_names: List of xcb.xproto.EventMask class variable names
    :rtype: void
    """
    masks = 0
    for mask_name in event_mask_names:
        assert hasattr(xproto.EventMask, mask_name)
        masks |= getattr(xproto.EventMask, mask_name)

    conn.core.ChangeWindowAttributesChecked(window, xproto.CW.EventMask,
                                            [masks]).check()

def get_parent_window(window):
    """
    Uses QueryTree() to find the parent of the given window.

    :param window: Window identifier.
    :return: Parent window identifier of 'window'.
    :rtype: int
    """
    return conn.core.QueryTree(window).reply().parent

def get_geometry(window, window_manager=None):
    """
    Returns the geometry of a window. This function will do its best to get
    the real geometry of a window; typically by inspecting the window's
    decorations if there are any.

    Since decorations are different for each window manager, you'll get the
    best possible results by passing a supported window manager in.

    :param window: Window identifier.
    :param window_manager: A class variable from Window.WindowManagers
    :type window_manager: int
    :return: Real geometry of a client window starting from the top-left corner.
    :rtype: (top_left_x, top_left_y, width, height)
    """

    if window_manager is WindowManagers.KWin:
        p = get_parent_window(window)
        return __get_geometry(get_parent_window(p))
    else:
        return __get_geometry(get_parent_window(window))

def moveresize(win, x=None, y=None, w=None, h=None, window_manager=None):
    """
    This function attempts to properly move/resize a window, accounting for
    its decorations.

    It doesn't rely upon _NET_FRAME_EXTENTS, but instead, uses the actual
    parent window to adjust the width and height. (I've found _NET_FRAME_EXTENTS
    to be wildly unreliable.)

    :param win: Window identifier.
    :param x: Top left x coordinate.
    :param y: Top left y coordinate.
    :param w: Client width.
    :param h: Client height.
    :param window_manager: A class variable from Window.WindowManagers
    :type window_manager: int
    :rtype: void
    """
    if window_manager is WindowManagers.KWin:
        tomove = get_parent_window(get_parent_window(win))
    else:
        tomove = get_parent_window(win)

    if tomove:
        cx, cy, cw, ch = __get_geometry(win)
        px, py, pw, ph = __get_geometry(tomove)

        w -= pw - cw
        h -= ph - ch

    ewmh.request_moveresize_window(win, x=x, y=y, width=max(1, w),
                                   height=max(1, h), source=2)

def __get_geometry(win):
    """
    Private function that abstracts the low level GetGeometry call.

    If you're looking for the size of a window including its decorations,
    please use ``window.get_geometry``.

    :param win: Window identifier.
    :return: X rectangle of the window.
    :rtype: (x, y, width, height)
    """
    raw = conn.core.GetGeometry(win).reply()
    return raw.x, raw.y, raw.width, raw.height

