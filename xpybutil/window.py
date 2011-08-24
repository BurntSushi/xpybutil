import xcb.xproto

from xpybutil import conn
import util

class WindowManagers(object):
    Unknown = 0
    Openbox = 1
    KWin = 2

def listen(window, *event_mask_names):
    masks = 0
    for mask_name in event_mask_names:
        assert hasattr(xcb.xproto.EventMask, mask_name)
        masks |= getattr(xcb.xproto.EventMask, mask_name)

    conn.core.ChangeWindowAttributesChecked(window, xcb.xproto.CW.EventMask, 
                                            [masks]).check()

def _get_geometry(win):
    raw = conn.core.GetGeometry(win).reply()
    return raw.x, raw.y, raw.width, raw.height

def get_geometry(window, window_manager=None):
    '''
    Returns the geometry of a window. This function will do its best to get
    the real geometry of a window; typically by inspecting the window's
    decorations if there are any.

    Since decorations are different for each window manager, you'll get the
    best possible results by passing a supported window manager in.
    '''

    if window_manager is WindowManagers.KWin:
        p = util.get_parent_window(window)
        return _get_geometry(conn, util.get_parent_window(p))
    else:
        return _get_geometry(conn, util.get_parent_window(window))

def moveresize(win, x=None, y=None, w=None, h=None, window_manager=None):
    '''
    This function attempts to properly move/resize a window, accounting for
    its decorations.

    It doesn't rely upon _NET_FRAME_EXTENTS, but instead, uses the actual
    parent window to adjust the width and height.
    '''
    import ewmh

    if window_manager is WindowManagers.KWin:
        tomove = util.get_parent_window(util.get_parent_window(win))
    else:
        tomove = util.get_parent_window(win)

    if tomove:
        cx, cy, cw, ch = _get_geometry(win)
        px, py, pw, ph = _get_geometry(tomove)

        w -= pw - cw
        h -= ph - ch

    ewmh.request_moveresize_window(win, x=x, y=y, width=max(1, w), 
                                   height=max(1, h), source=2)

