import struct
import time

import xcb.xproto

import util

__atoms = [
           # Root Window Properties (and Related Messages)
           '_NET_SUPPORTED', '_NET_CLIENT_LIST', '_NET_CLIENT_LIST_STACKING',
           '_NET_NUMBER_OF_DESKTOPS', '_NET_DESKTOP_GEOMETRY',
           '_NET_DESKTOP_VIEWPORT', '_NET_CURRENT_DESKTOP',
           '_NET_DESKTOP_NAMES', '_NET_ACTIVE_WINDOW', '_NET_WORKAREA',
           '_NET_SUPPORTING_WM_CHECK', '_NET_VIRTUAL_ROOTS',
           '_NET_DESKTOP_LAYOUT', '_NET_SHOWING_DESKTOP',

           # Other Root Window Messages
           '_NET_CLOSE_WINDOW', '_NET_MORERESIZE_WINDOW', '_NET_WM_MOVERESIZE',
           '_NET_RESTACK_WINDOW', '_NET_REQUEST_FRAME_EXTENTS',

           # Application Window Properties
           '_NET_WM_NAME', '_NET_WM_VISIBLE_NAME', '_NET_WM_ICON_NAME',
           '_NET_WM_VISIBLE_ICON_NAME', '_NET_WM_DESKTOP',
           '_NET_WM_WINDOW_TYPE', '_NET_WM_STATE', '_NET_WM_ALLOWED_ACTIONS',
           '_NET_WM_STRUT', '_NET_WM_STRUT_PARTIAL', '_NET_WM_ICON_GEOMETRY',
           '_NET_WM_ICON', '_NET_WM_PID', '_NET_WM_HANDLED_ICONS',
           '_NET_WM_USER_TIME', '_NET_WM_USER_TIME_WINDOW',
           '_NET_FRAME_EXTENTS',

           # Window Manager Protocols
           '_NET_WM_PING', '_NET_WM_SYNC_REQUEST',
           '_NET_WM_FULLSCREEN_MONITORS',

           # Other Properties
           '_NET_WM_FULL_PLACEMENT',

           # _NET_WM_WINDOW_TYPE_*
           '_NET_WM_WINDOW_TYPE_DESKTOP', '_NET_WM_WINDOW_TYPE_DOCK',
           '_NET_WM_WINDOW_TYPE_TOOLBAR', '_NET_WM_WINDOW_TYPE_MENU',
           '_NET_WM_WINDOW_TYPE_UTILITY', '_NET_WM_WINDOW_TYPE_SPLASH',
           '_NET_WM_WINDOW_TYPE_DIALOG', '_NET_WM_WINDOW_TYPE_DROPDOWN_MENU',
           '_NET_WM_WINDOW_TYPE_POPUP_MENU', '_NET_WM_WINDOW_TYPE_TOOLTIP',
           '_NET_WM_WINDOW_TYPE_NOTIFICATION', '_NET_WM_WINDOW_TYPE_COMBO',
           '_NET_WM_WINDOW_TYPE_DND', '_NET_WM_WINDOW_TYPE_NORMAL',

           # _NET_WM_STATE_*
           '_NET_WM_STATE_MODAL', '_NET_WM_STATE_STICKY',
           '_NET_WM_STATE_MAXIMIZED_VERT', '_NET_WM_STATE_MAXIMIZED_HORZ',
           '_NET_WM_STATE_SHADED', '_NET_WM_STATE_SKIP_TASKBAR',
           '_NET_WM_STATE_SKIP_PAGER', '_NET_WM_STATE_HIDDEN',
           '_NET_WM_STATE_FULLSCREEN', '_NET_WM_STATE_ABOVE',
           '_NET_WM_STATE_BELOW', '_NET_WM_STATE_DEMANDS_ATTENTION',

           # _NET_WM_ACTION_*
           '_NET_WM_ACTION_MOVE', '_NET_WM_ACTION_RESIZE',
           '_NET_WM_ACTION_MINIMIZE', '_NET_WM_ACTION_SHADE',
           '_NET_WM_ACTION_STICK', '_NET_WM_ACTION_MAXIMIZE_HORZ',
           '_NET_WM_ACTION_MAXIMIZE_VERT', '_NET_WM_ACTION_FULLSCREEN',
           '_NET_WM_ACTION_CHANGE_DESKTOP', '_NET_WM_ACTION_CLOSE',
           '_NET_WM_ACTION_ABOVE', '_NET_WM_ACTION_BELOW',

           # Additional TEXT Type
           'UTF8_STRING'
           ]

class Orientation:
    Horz = 0
    Vert = 1

class StartingCorner:
    TopLeft = 0
    TopRight = 1
    BottomRight = 2
    BottomLeft = 3

class MoveResize:
    SizeTopLeft = 0
    SizeTop = 1
    SizeTopRight = 2
    SizeRight = 3
    SizeBottomRight = 4
    SizeBottom = 5
    SizeBottomLeft = 6
    SizeLeft = 7
    Move = 8
    SizeKeyboard = 9
    MoveKeyboard = 10
    Cancel = 11

# Handle atom caching
def build_atom_cache(c):
    for atom in __atoms:
        util.__atom_cache[atom] = util.get_atom_cookie(c, atom,
                                                       only_if_exists=False)

# Some aliases
atom = util.get_atom
root = util.get_root
revent = util.root_send_client_event
revent_checked = util.root_send_client_event_checked
CARDINAL = xcb.xproto.Atom.CARDINAL

# _NET_SUPPORTED

def get_supported(c, window):
    """
    Returns a list of hints supported by the window manager.

    This property MUST be set by the Window Manager to indicate which hints
    it supports. For example: considering _NET_WM_STATE both this atom and
    all supported states e.g. _NET_WM_STATE_MODAL, _NET_WM_STATE_STICKY,
    would be listed. This assumes that backwards incompatible changes will
    not be made to the hints (without being renamed).

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @return:        A list of atoms in the _NET_SUPPORTED property.
    @rtype:         util.PropertyCookie (ATOM[]/32)
    """
    return util.PropertyCookie(
        util.get_property(c, window, atom(c, '_NET_SUPPORTED')))

def get_supported_unchecked(c, window):
    """
    Returns a list of hints supported by the window manager.

    This property MUST be set by the Window Manager to indicate which hints
    it supports. For example: considering _NET_WM_STATE both this atom and
    all supported states e.g. _NET_WM_STATE_MODAL, _NET_WM_STATE_STICKY,
    would be listed. This assumes that backwards incompatible changes will
    not be made to the hints (without being renamed).

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @return:        A list of atoms in the _NET_SUPPORTED property.
    @rtype:         util.PropertyCookie (ATOM[]/32)
    """
    return util.PropertyCookie(
        util.get_property_unchecked(c, window, atom(c, '_NET_SUPPORTED')))

def set_supported(c, window, atoms):
    """
    Sets the list of hints supported by the window manager.

    This property MUST be set by the Window Manager to indicate which hints
    it supports. For example: considering _NET_WM_STATE both this atom and
    all supported states e.g. _NET_WM_STATE_MODAL, _NET_WM_STATE_STICKY,
    would be listed. This assumes that backwards incompatible changes will
    not be made to the hints (without being renamed).

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @param atoms:   A list of atom identifiers.
    @type atoms:    ATOM[]/32
    @rtype:         xcb.VoidCookie
    """
    packed = struct.pack('I' * len(atoms), *atoms)
    return c.core.ChangeProperty(xcb.xproto.PropMode.Replace, window,
                                 atom(c, '_NET_SUPPORTED'),
                                 xcb.xproto.Atom.ATOM, 32, len(atoms),
                                 packed)

def set_supported_checked(c, window, atoms):
    """
    Sets the list of hints supported by the window manager.

    This property MUST be set by the Window Manager to indicate which hints
    it supports. For example: considering _NET_WM_STATE both this atom and
    all supported states e.g. _NET_WM_STATE_MODAL, _NET_WM_STATE_STICKY,
    would be listed. This assumes that backwards incompatible changes will
    not be made to the hints (without being renamed).

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @param atoms:   A list of atom identifiers.
    @type atoms:    ATOM[]/32
    @rtype:         xcb.VoidCookie
    """
    packed = struct.pack('I' * len(atoms), *atoms)
    return c.core.ChangePropertyChecked(xcb.xproto.PropMode.Replace, window,
                                 atom(c, '_NET_SUPPORTED'),
                                 xcb.xproto.Atom.ATOM, 32, len(atoms),
                                 packed)

# _NET_CLIENT_LIST

def get_client_list(c, window):
    """
    Returns a list of windows managed by the window manager.

    These arrays contain all X Windows managed by the Window Manager.
    _NET_CLIENT_LIST has initial mapping order, starting with the oldest
    window. _NET_CLIENT_LIST_STACKING has bottom-to-top stacking order.
    These properties SHOULD be set and updated by the Window Manager.

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @return:        A list of window identifiers.
    @rtype:         util.PropertyCookie (ATOM[]/32)
    """
    return util.PropertyCookie(
        util.get_property(c, window, atom(c, '_NET_CLIENT_LIST')))

def get_client_list_unchecked(c, window):
    """
    Returns a list of windows managed by the window manager.

    These arrays contain all X Windows managed by the Window Manager.
    _NET_CLIENT_LIST has initial mapping order, starting with the oldest
    window. _NET_CLIENT_LIST_STACKING has bottom-to-top stacking order.
    These properties SHOULD be set and updated by the Window Manager.

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @return:        A list of window identifiers.
    @rtype:         util.PropertyCookie (ATOM[]/32)
    """
    return util.PropertyCookie(
        util.get_property_unchecked(c, window, atom(c, '_NET_CLIENT_LIST')))

def set_client_list(c, window, windows):
    """
    Sets the list of windows managed by the window manager.

    These arrays contain all X Windows managed by the Window Manager.
    _NET_CLIENT_LIST has initial mapping order, starting with the oldest
    window. _NET_CLIENT_LIST_STACKING has bottom-to-top stacking order.
    These properties SHOULD be set and updated by the Window Manager.

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @param windows: A list of atom identifiers.
    @type windows:  ATOM[]/32
    @rtype:         xcb.VoidCookie
    """
    packed = struct.pack('I' * len(windows), *windows)
    return c.core.ChangeProperty(xcb.xproto.PropMode.Replace, window,
                                 atom(c, '_NET_CLIENT_LIST'),
                                 xcb.xproto.Atom.WINDOW, 32, len(windows),
                                 packed)

def set_client_list_checked(c, window, windows):
    """
    Sets the list of windows managed by the window manager.

    These arrays contain all X Windows managed by the Window Manager.
    _NET_CLIENT_LIST has initial mapping order, starting with the oldest
    window. _NET_CLIENT_LIST_STACKING has bottom-to-top stacking order.
    These properties SHOULD be set and updated by the Window Manager.

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @param windows: A list of atom identifiers.
    @type windows:  ATOM[]/32
    @rtype:         xcb.VoidCookie
    """
    packed = struct.pack('I' * len(windows), *windows)
    return c.core.ChangePropertyChecked(xcb.xproto.PropMode.Replace, window,
                                 atom(c, '_NET_CLIENT_LIST'),
                                 xcb.xproto.Atom.WINDOW, 32, len(windows),
                                 packed)

# _NET_CLIENT_LIST_STACKING

def get_client_list_stacking(c, window):
    """
    Returns the window stacking order.

    These arrays contain all X Windows managed by the Window Manager.
    _NET_CLIENT_LIST has initial mapping order, starting with the oldest
    window. _NET_CLIENT_LIST_STACKING has bottom-to-top stacking order.
    These properties SHOULD be set and updated by the Window Manager.

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @return:        A list of window identifiers.
    @rtype:         util.PropertyCookie (ATOM[]/32)
    """
    return util.PropertyCookie(
        util.get_property(c, window, atom(c, '_NET_CLIENT_LIST_STACKING')))

def get_client_list_stacking_unchecked(c, window):
    """
    Returns the window stacking order.

    These arrays contain all X Windows managed by the Window Manager.
    _NET_CLIENT_LIST has initial mapping order, starting with the oldest
    window. _NET_CLIENT_LIST_STACKING has bottom-to-top stacking order.
    These properties SHOULD be set and updated by the Window Manager.

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @return:        A list of window identifiers.
    @rtype:         util.PropertyCookie (ATOM[]/32)
    """
    return util.PropertyCookie(
        util.get_property_unchecked(c, window,
                                    atom(c, '_NET_CLIENT_LIST_STACKING')))

def set_client_list_stacking(c, window, windows):
    """
    Sets the window stacking order.

    These arrays contain all X Windows managed by the Window Manager.
    _NET_CLIENT_LIST has initial mapping order, starting with the oldest
    window. _NET_CLIENT_LIST_STACKING has bottom-to-top stacking order.
    These properties SHOULD be set and updated by the Window Manager.

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @param windows: A list of atom identifiers.
    @type windows:  ATOM[]/32
    @rtype:         xcb.VoidCookie
    """
    packed = struct.pack('I' * len(windows), *windows)
    return c.core.ChangeProperty(xcb.xproto.PropMode.Replace, window,
                                 atom(c, '_NET_CLIENT_LIST_STACKING'),
                                 xcb.xproto.Atom.WINDOW, 32, len(windows),
                                 packed)

def set_client_list_stacking_checked(c, window, windows):
    """
    Sets the window stacking order.

    These arrays contain all X Windows managed by the Window Manager.
    _NET_CLIENT_LIST has initial mapping order, starting with the oldest
    window. _NET_CLIENT_LIST_STACKING has bottom-to-top stacking order.
    These properties SHOULD be set and updated by the Window Manager.

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @param windows: A list of atom identifiers.
    @type windows:  ATOM[]/32
    @rtype:         xcb.VoidCookie
    """
    packed = struct.pack('I' * len(windows), *windows)
    return c.core.ChangePropertyChecked(xcb.xproto.PropMode.Replace, window,
                                 atom(c, '_NET_CLIENT_LIST_STACKING'),
                                 xcb.xproto.Atom.WINDOW, 32, len(windows),
                                 packed)

# _NET_NUMBER_DESKTOPS

def get_number_of_desktops(c, window):
    """
    Returns the number of virtual desktops.

    This property SHOULD be set and updated by the Window Manager to
    indicate the number of virtual desktops.

    The Window Manager is free to honor or reject this request. If the
    request is honored _NET_NUMBER_OF_DESKTOPS MUST be set to the new
    number of desktops, _NET_VIRTUAL_ROOTS MUST be set to store the new
    number of desktop virtual root window IDs and _NET_DESKTOP_VIEWPORT and
    _NET_WORKAREA must also be changed accordingly. The _NET_DESKTOP_NAMES
    property MAY remain unchanged.

    If the number of desktops is shrinking and _NET_CURRENT_DESKTOP is out
    of the new range of available desktops, then this MUST be set to the
    last available desktop from the new set. Clients that are still present
    on desktops that are out of the new range MUST be moved to the very
    last desktop from the new set. For these _NET_WM_DESKTOP MUST be updated.

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @return:        The number of desktops.
    @rtype:         util.PropertyCookieSingle (CARDINAL/32)
    """
    return util.PropertyCookieSingle(
        util.get_property(c, window, atom(c, '_NET_NUMBER_OF_DESKTOPS')))

def get_number_of_desktops_unchecked(c, window):
    """
    Returns the number of virtual desktops.

    This property SHOULD be set and updated by the Window Manager to
    indicate the number of virtual desktops.

    The Window Manager is free to honor or reject this request. If the
    request is honored _NET_NUMBER_OF_DESKTOPS MUST be set to the new
    number of desktops, _NET_VIRTUAL_ROOTS MUST be set to store the new
    number of desktop virtual root window IDs and _NET_DESKTOP_VIEWPORT and
    _NET_WORKAREA must also be changed accordingly. The _NET_DESKTOP_NAMES
    property MAY remain unchanged.

    If the number of desktops is shrinking and _NET_CURRENT_DESKTOP is out
    of the new range of available desktops, then this MUST be set to the
    last available desktop from the new set. Clients that are still present
    on desktops that are out of the new range MUST be moved to the very
    last desktop from the new set. For these _NET_WM_DESKTOP MUST be updated.

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @return:        The number of desktops.
    @rtype:         util.PropertyCookieSingle (CARDINAL/32)
    """
    return util.PropertyCookieSingle(
        util.get_property_unchecked(c, window,
                                    atom(c, '_NET_NUMBER_OF_DESKTOPS')))

def set_number_of_desktops(c, window, number_of_desktops):
    """
    Sets the number of desktops.

    This property SHOULD be set and updated by the Window Manager to
    indicate the number of virtual desktops.

    The Window Manager is free to honor or reject this request. If the
    request is honored _NET_NUMBER_OF_DESKTOPS MUST be set to the new
    number of desktops, _NET_VIRTUAL_ROOTS MUST be set to store the new
    number of desktop virtual root window IDs and _NET_DESKTOP_VIEWPORT and
    _NET_WORKAREA must also be changed accordingly. The _NET_DESKTOP_NAMES
    property MAY remain unchanged.

    If the number of desktops is shrinking and _NET_CURRENT_DESKTOP is out
    of the new range of available desktops, then this MUST be set to the
    last available desktop from the new set. Clients that are still present
    on desktops that are out of the new range MUST be moved to the very
    last desktop from the new set. For these _NET_WM_DESKTOP MUST be updated.

    @param c:                   An xpyb connection object.
    @param window:              A window identifier.
    @param number_of_desktops:  The number of desktops.
    @type number_of_desktops:   CARDINAL/32
    @rtype:                     xcb.VoidCookie
    """
    return c.core.ChangeProperty(xcb.xproto.PropMode.Replace, window,
                                 atom(c, '_NET_NUMBER_OF_DESKTOPS'),
                                 CARDINAL, 32, len(str(number_of_desktops)),
                                 [number_of_desktops])

def set_number_of_desktops_checked(c, window, number_of_desktops):
    """
    Sets the number of desktops.

    This property SHOULD be set and updated by the Window Manager to
    indicate the number of virtual desktops.

    The Window Manager is free to honor or reject this request. If the
    request is honored _NET_NUMBER_OF_DESKTOPS MUST be set to the new
    number of desktops, _NET_VIRTUAL_ROOTS MUST be set to store the new
    number of desktop virtual root window IDs and _NET_DESKTOP_VIEWPORT and
    _NET_WORKAREA must also be changed accordingly. The _NET_DESKTOP_NAMES
    property MAY remain unchanged.

    If the number of desktops is shrinking and _NET_CURRENT_DESKTOP is out
    of the new range of available desktops, then this MUST be set to the
    last available desktop from the new set. Clients that are still present
    on desktops that are out of the new range MUST be moved to the very
    last desktop from the new set. For these _NET_WM_DESKTOP MUST be updated.

    @param c:                   An xpyb connection object.
    @param window:              A window identifier.
    @param number_of_desktops:  The number of desktops.
    @type number_of_desktops:   CARDINAL/32
    @rtype:                     xcb.VoidCookie
    """
    return c.core.ChangePropertyChecked(xcb.xproto.PropMode.Replace, window,
                                 atom(c, '_NET_NUMBER_OF_DESKTOPS'),
                                 CARDINAL, 32, len(str(number_of_desktops)),
                                 [number_of_desktops])

def request_number_of_desktops(c, number_of_desktops):
    """
    Sends event to root window to set the number of desktops.

    This property SHOULD be set and updated by the Window Manager to
    indicate the number of virtual desktops.

    The Window Manager is free to honor or reject this request. If the
    request is honored _NET_NUMBER_OF_DESKTOPS MUST be set to the new
    number of desktops, _NET_VIRTUAL_ROOTS MUST be set to store the new
    number of desktop virtual root window IDs and _NET_DESKTOP_VIEWPORT and
    _NET_WORKAREA must also be changed accordingly. The _NET_DESKTOP_NAMES
    property MAY remain unchanged.

    If the number of desktops is shrinking and _NET_CURRENT_DESKTOP is out
    of the new range of available desktops, then this MUST be set to the
    last available desktop from the new set. Clients that are still present
    on desktops that are out of the new range MUST be moved to the very
    last desktop from the new set. For these _NET_WM_DESKTOP MUST be updated.

    @param c:                   An xpyb connection object.
    @param number_of_desktops:  The number of desktops.
    @type number_of_desktops:   CARDINAL/32
    @rtype:                     xcb.VoidCookie
    """
    return revent(c, root(c), atom(c, '_NET_NUMBER_OF_DESKTOPS'),
                  [number_of_desktops])

def request_number_of_desktops_checked(c, number_of_desktops):
    """
    Sends event to root window to set the number of desktops.

    This property SHOULD be set and updated by the Window Manager to
    indicate the number of virtual desktops.

    The Window Manager is free to honor or reject this request. If the
    request is honored _NET_NUMBER_OF_DESKTOPS MUST be set to the new
    number of desktops, _NET_VIRTUAL_ROOTS MUST be set to store the new
    number of desktop virtual root window IDs and _NET_DESKTOP_VIEWPORT and
    _NET_WORKAREA must also be changed accordingly. The _NET_DESKTOP_NAMES
    property MAY remain unchanged.

    If the number of desktops is shrinking and _NET_CURRENT_DESKTOP is out
    of the new range of available desktops, then this MUST be set to the
    last available desktop from the new set. Clients that are still present
    on desktops that are out of the new range MUST be moved to the very
    last desktop from the new set. For these _NET_WM_DESKTOP MUST be updated.

    @param c:                   An xpyb connection object.
    @param number_of_desktops:  The number of desktops.
    @type number_of_desktops:   CARDINAL/32
    @rtype:                     xcb.VoidCookie
    """
    return revent_checked(c, root(c), atom(c, '_NET_NUMBER_OF_DESKTOPS'),
                          [number_of_desktops])

# _NET_DESKTOP_GEOMETRY

class DesktopGeometryCookie(util.PropertyCookie):
    def reply(self):
        v = util.PropertyCookie.reply(self)

        if not v:
            return None

        return {
            'width': v[0],
            'height': v[1]
        }

def get_desktop_geometry(c, window):
    """
    Returns the desktop geometry.

    Array of two cardinals that defines the common size of all desktops
    (this is equal to the screen size if the Window Manager doesn't support
    large desktops, otherwise it's equal to the virtual size of the
    desktop). This property SHOULD be set by the Window Manager.

    The Window Manager MAY choose to ignore this message, in which case
    _NET_DESKTOP_GEOMETRY property will remain unchanged.

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @return:        A desktop geometry dictionary.

                    Keys: width, height
    @rtype:         DesktopGeometryCookie (CARDINAL[2]/32)
    """
    return DesktopGeometryCookie(
        util.get_property(c, window, atom(c, '_NET_DESKTOP_GEOMETRY')))

def get_desktop_geometry_unchecked(c, window):
    """
    Returns the desktop geometry.

    Array of two cardinals that defines the common size of all desktops
    (this is equal to the screen size if the Window Manager doesn't support
    large desktops, otherwise it's equal to the virtual size of the
    desktop). This property SHOULD be set by the Window Manager.

    The Window Manager MAY choose to ignore this message, in which case
    _NET_DESKTOP_GEOMETRY property will remain unchanged.

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @return:        A desktop geometry dictionary.

                    Keys: width, height
    @rtype:         DesktopGeometryCookie (CARDINAL[2]/32)
    """
    return DesktopGeometryCookie(
        util.get_property_unchecked(c, window,
                                    atom(c, '_NET_DESKTOP_GEOMETRY')))

def set_desktop_geometry(c, window, width, height):
    """
    Sets the desktop geometry.

    Array of two cardinals that defines the common size of all desktops
    (this is equal to the screen size if the Window Manager doesn't support
    large desktops, otherwise it's equal to the virtual size of the
    desktop). This property SHOULD be set by the Window Manager.

    The Window Manager MAY choose to ignore this message, in which case
    _NET_DESKTOP_GEOMETRY property will remain unchanged.

    @param c:                   An xpyb connection object.
    @param window:              A window identifier.
    @param width:               The width of the desktop.
    @type width:                CARDINAL/32
    @param height:              The height of the desktop.
    @type height:               CARDINAL/32
    @rtype:                     xcb.VoidCookie
    """
    packed = struct.pack('II', width, height)
    return c.core.ChangeProperty(xcb.xproto.PropMode.Replace, window,
                                 atom(c, '_NET_DESKTOP_GEOMETRY'),
                                 CARDINAL, 32, 2,
                                 packed)

def set_desktop_geometry_checked(c, window, width, height):
    """
    Sets the desktop geometry.

    Array of two cardinals that defines the common size of all desktops
    (this is equal to the screen size if the Window Manager doesn't support
    large desktops, otherwise it's equal to the virtual size of the
    desktop). This property SHOULD be set by the Window Manager.

    The Window Manager MAY choose to ignore this message, in which case
    _NET_DESKTOP_GEOMETRY property will remain unchanged.

    @param c:                   An xpyb connection object.
    @param window:              A window identifier.
    @param width:               The width of the desktop.
    @type width:                CARDINAL/32
    @param height:              The height of the desktop.
    @type height:               CARDINAL/32
    @rtype:                     xcb.VoidCookie
    """
    packed = struct.pack('II', width, height)
    return c.core.ChangePropertyChecked(xcb.xproto.PropMode.Replace, window,
                                 atom(c, '_NET_DESKTOP_GEOMETRY'),
                                 CARDINAL, 32, 2,
                                 packed)

def request_desktop_geometry(c, width, height):
    """
    Sends event to root window to set the desktop geometry.

    Array of two cardinals that defines the common size of all desktops
    (this is equal to the screen size if the Window Manager doesn't support
    large desktops, otherwise it's equal to the virtual size of the
    desktop). This property SHOULD be set by the Window Manager.

    The Window Manager MAY choose to ignore this message, in which case
    _NET_DESKTOP_GEOMETRY property will remain unchanged.

    @param c:                   An xpyb connection object.
    @param width:               The width of the desktop.
    @type width:                CARDINAL/32
    @param height:              The height of the desktop.
    @type height:               CARDINAL/32
    @rtype:                     xcb.VoidCookie
    """
    return revent(c, root(c), atom(c, '_NET_NUMBER_OF_DESKTOPS'),
                  [width, height])

def request_desktop_geometry_checked(c, width, height):
    """
    Sends event to root window to set the desktop geometry.

    Array of two cardinals that defines the common size of all desktops
    (this is equal to the screen size if the Window Manager doesn't support
    large desktops, otherwise it's equal to the virtual size of the
    desktop). This property SHOULD be set by the Window Manager.

    The Window Manager MAY choose to ignore this message, in which case
    _NET_DESKTOP_GEOMETRY property will remain unchanged.

    @param c:                   An xpyb connection object.
    @param width:               The width of the desktop.
    @type width:                CARDINAL/32
    @param height:              The height of the desktop.
    @type height:               CARDINAL/32
    @rtype:                     xcb.VoidCookie
    """
    return revent_checked(c, root(c), atom(c, '_NET_NUMBER_OF_DESKTOPS'),
                  [width, height])

# _NET_DESKTOP_VIEWPORT

class DesktopViewportCookie(util.PropertyCookie):
    def reply(self):
        v = util.PropertyCookie.reply(self)

        if not v:
            return None

        ret = []
        for i in xrange(0, len(v), 2):
            ret.append({
                'x': v[i],
                'y': v[i + 1]
            })

        return ret

def get_desktop_viewport(c, window):
    """
    Returns x,y pairs defining the top-left corner of each desktop's viewport.

    Array of pairs of cardinals that define the top left corner of each
    desktop's viewport. For Window Managers that don't support large
    desktops, this MUST always be set to (0,0).

    The Window Manager MAY choose to ignore this message, in which case
    _NET_DESKTOP_VIEWPORT property will remain unchanged.

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @return:        A list of desktop viewport dictionaries.

                    Keys: x, y
    @rtype:         DesktopViewportCookie (CARDINAL[][2]/32)
    """
    return DesktopViewportCookie(
        util.get_property(c, window, atom(c, '_NET_DESKTOP_VIEWPORT')))

def get_desktop_viewport_unchecked(c, window):
    """
    Returns x,y pairs defining the top-left corner of each desktop's viewport.

    Array of pairs of cardinals that define the top left corner of each
    desktop's viewport. For Window Managers that don't support large
    desktops, this MUST always be set to (0,0).

    The Window Manager MAY choose to ignore this message, in which case
    _NET_DESKTOP_VIEWPORT property will remain unchanged.

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @return:        A list of desktop viewport dictionaries.

                    Keys: x, y
    @rtype:         DesktopViewportCookie (CARDINAL[][2]/32)
    """
    return DesktopViewportCookie(
        util.get_property_unchecked(c, window,
                                    atom(c, '_NET_DESKTOP_VIEWPORT')))

def set_desktop_viewport(c, window, pairs):
    """
    Sets the x,y pairs defining the top-left corner of each desktop's viewport.

    Array of pairs of cardinals that define the top left corner of each
    desktop's viewport. For Window Managers that don't support large
    desktops, this MUST always be set to (0,0).

    The Window Manager MAY choose to ignore this message, in which case
    _NET_DESKTOP_VIEWPORT property will remain unchanged.

    Pairs should look like:

        >>> [
        {'x': 0, 'y': 0},
        {'x': 500, 'y': 500},
        ...
        ]

    Which would set desktop 0's viewport top-left corner to 0,0 and desktop
    1's viewport top-left corner to 500,500.

    @param c:                   An xpyb connection object.
    @param window:              A window identifier.
    @param pairs:               A list of x,y dictionary pairs.
    @type pairs:                CARDINAL[][2]/32
    @rtype:                     xcb.VoidCookie
    """
    flatten = []
    for pair in pairs:
        flatten.append(pair['x'])
        flatten.append(pair['y'])

    packed = struct.pack('I' * len(flatten), *flatten)
    return c.core.ChangeProperty(xcb.xproto.PropMode.Replace, window,
                                 atom(c, '_NET_DESKTOP_VIEWPORT'),
                                 CARDINAL, 32, len(flatten),
                                 packed)

def set_desktop_viewport_checked(c, window, pairs):
    """
    Sets the x,y pairs defining the top-left corner of each desktop's viewport.

    Array of pairs of cardinals that define the top left corner of each
    desktop's viewport. For Window Managers that don't support large
    desktops, this MUST always be set to (0,0).

    The Window Manager MAY choose to ignore this message, in which case
    _NET_DESKTOP_VIEWPORT property will remain unchanged.

    Pairs should look like:

        >>> [
        {'x': 0, 'y': 0},
        {'x': 500, 'y': 500},
        ...
        ]

    Which would set desktop 0's viewport top-left corner to 0,0 and desktop
    1's viewport top-left corner to 500,500.

    @param c:                   An xpyb connection object.
    @param window:              A window identifier.
    @param pairs:               A list of x,y dictionary pairs.
    @type pairs:                CARDINAL[][2]/32
    @rtype:                     xcb.VoidCookie
    """
    flatten = []
    for pair in pairs:
        flatten.append(pair['x'])
        flatten.append(pair['y'])

    packed = struct.pack('I' * len(flatten), *flatten)
    return c.core.ChangePropertyChecked(xcb.xproto.PropMode.Replace, window,
                                 atom(c, '_NET_DESKTOP_VIEWPORT'),
                                 CARDINAL, 32, len(flatten),
                                 packed)

def request_desktop_viewport(c, x, y):
    """
    Sends event to root window to set the viewport position of current desktop.

    Array of pairs of cardinals that define the top left corner of each
    desktop's viewport. For Window Managers that don't support large
    desktops, this MUST always be set to (0,0).

    The Window Manager MAY choose to ignore this message, in which case
    _NET_DESKTOP_VIEWPORT property will remain unchanged.

    @param c:       An xpyb connection object.
    @param x:       The x position of the top-left corner.
    @type x:        CARDINAL/32
    @param y:       The y position of the top-left corner.
    @type y:        CARDINAL/32
    @rtype:         xcb.VoidCookie
    """
    return revent(c, root(c), atom(c, '_NET_DESKTOP_VIEWPORT'),
                  [x, y])

def request_desktop_viewport_checked(c, x, y):
    """
    Sends event to root window to set the viewport position of current desktop.

    Array of pairs of cardinals that define the top left corner of each
    desktop's viewport. For Window Managers that don't support large
    desktops, this MUST always be set to (0,0).

    The Window Manager MAY choose to ignore this message, in which case
    _NET_DESKTOP_VIEWPORT property will remain unchanged.

    @param c:       An xpyb connection object.
    @param x:       The x position of the top-left corner.
    @type x:        CARDINAL/32
    @param y:       The y position of the top-left corner.
    @type y:        CARDINAL/32
    @rtype:         xcb.VoidCookie
    """
    return revent_checked(c, root(c), atom(c, '_NET_DESKTOP_VIEWPORT'),
                  [x, y])

# _NET_CURRENT_DESKTOP

def get_current_desktop(c, window):
    """
    Returns the current desktop number.

    The index of the current desktop. This is always an integer between 0
    and _NET_NUMBER_OF_DESKTOPS - 1. This MUST be set and updated by the
    Window Manager.

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @return:        The index of the current desktop.
    @rtype:         util.PropertyCookieSingle (CARDINAL/32)
    """
    return util.PropertyCookieSingle(
        util.get_property(c, window, atom(c, '_NET_CURRENT_DESKTOP')))

def get_current_desktop_unchecked(c, window):
    """
    Returns the current desktop number.

    The index of the current desktop. This is always an integer between 0
    and _NET_NUMBER_OF_DESKTOPS - 1. This MUST be set and updated by the
    Window Manager.

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @return:        The index of the current desktop.
    @rtype:         util.PropertyCookieSingle (CARDINAL/32)
    """
    return util.PropertyCookieSingle(
        util.get_property_unchecked(c, window,
                                    atom(c, '_NET_CURRENT_DESKTOP')))

def set_current_desktop(c, window, current_desktop):
    """
    Sets the current desktop number.

    The index of the current desktop. This is always an integer between 0
    and _NET_NUMBER_OF_DESKTOPS - 1. This MUST be set and updated by the
    Window Manager.

    @param c:                   An xpyb connection object.
    @param window:              A window identifier.
    @param current_desktop:     The current desktop index.
    @type current_desktop:      CARDINAL/32
    @rtype:                     xcb.VoidCookie
    """
    return c.core.ChangeProperty(xcb.xproto.PropMode.Replace, window,
                                 atom(c, '_NET_CURRENT_DESKTOP'),
                                 CARDINAL, 32, len(str(current_desktop)),
                                 [current_desktop])

def set_current_desktop_checked(c, window, current_desktop):
    """
    Sets the current desktop number.

    The index of the current desktop. This is always an integer between 0
    and _NET_NUMBER_OF_DESKTOPS - 1. This MUST be set and updated by the
    Window Manager.

    @param c:                   An xpyb connection object.
    @param window:              A window identifier.
    @param current_desktop:     The current desktop index.
    @type current_desktop:      CARDINAL/32
    @rtype:                     xcb.VoidCookie
    """
    return c.core.ChangePropertyChecked(xcb.xproto.PropMode.Replace, window,
                                 atom(c, '_NET_CURRENT_DESKTOP'),
                                 CARDINAL, 32, len(str(current_desktop)),
                                 [current_desktop])

def request_current_desktop(c, desktop_number,
                            timestamp=xcb.xproto.Time.CurrentTime):
    """
    Sends event to root window to set the current desktop.

    The index of the current desktop. This is always an integer between 0
    and _NET_NUMBER_OF_DESKTOPS - 1. This MUST be set and updated by the
    Window Manager.

    @param c:                   An xpyb connection object.
    @param desktop_number:      The current desktop index.
    @type desktop_number:       CARDINAL/32
    @type timestamp:            Milliseconds.
    @rtype:                     xcb.VoidCookie
    """
    return revent(c, root(c), atom(c, '_NET_CURRENT_DESKTOP'),
                  [desktop_number, timestamp])

def request_current_desktop_checked(c, desktop_number,
                                    timestamp=xcb.xproto.Time.CurrentTime):
    """
    Sends event to root window to set the current desktop.

    The index of the current desktop. This is always an integer between 0
    and _NET_NUMBER_OF_DESKTOPS - 1. This MUST be set and updated by the
    Window Manager.

    @param c:                   An xpyb connection object.
    @param desktop_number:      The current desktop index.
    @type desktop_number:       CARDINAL/32
    @type timestamp:            Milliseconds.
    @rtype:                     xcb.VoidCookie
    """
    return revent_checked(c, root(c), atom(c, '_NET_CURRENT_DESKTOP'),
                  [desktop_number, timestamp])

# _NET_DESKTOP_NAMES

def get_desktop_names(c, window):
    """
    Returns a list of names of the virtual desktops.

    The names of all virtual desktops. This is a list of NULL-terminated
    strings in UTF-8 encoding [UTF8]. This property MAY be changed by a
    Pager or the Window Manager at any time.

    Note: The number of names could be different from
    _NET_NUMBER_OF_DESKTOPS. If it is less than _NET_NUMBER_OF_DESKTOPS,
    then the desktops with high numbers are unnamed. If it is larger than
    _NET_NUMBER_OF_DESKTOPS, then the excess names outside of the
    _NET_NUMBER_OF_DESKTOPS are considered to be reserved in case the
    number of desktops is increased.

    Rationale: The name is not a necessary attribute of a virtual desktop.
    Thus the availability or unavailability of names has no impact on
    virtual desktop functionality. Since names are set by users and users
    are likely to preset names for a fixed number of desktops, it doesn't
    make sense to shrink or grow this list when the number of available
    desktops changes.

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @return:        A list of virutal desktop names.
    @rtype:         util.PropertyCookie (UTF8_STRING[])
    """
    return util.PropertyCookie(
        util.get_property(c, window, atom(c, '_NET_DESKTOP_NAMES')))

def get_desktop_names_unchecked(c, window):
    """
    Returns a list of names of the virtual desktops.

    The names of all virtual desktops. This is a list of NULL-terminated
    strings in UTF-8 encoding [UTF8]. This property MAY be changed by a
    Pager or the Window Manager at any time.

    Note: The number of names could be different from
    _NET_NUMBER_OF_DESKTOPS. If it is less than _NET_NUMBER_OF_DESKTOPS,
    then the desktops with high numbers are unnamed. If it is larger than
    _NET_NUMBER_OF_DESKTOPS, then the excess names outside of the
    _NET_NUMBER_OF_DESKTOPS are considered to be reserved in case the
    number of desktops is increased.

    Rationale: The name is not a necessary attribute of a virtual desktop.
    Thus the availability or unavailability of names has no impact on
    virtual desktop functionality. Since names are set by users and users
    are likely to preset names for a fixed number of desktops, it doesn't
    make sense to shrink or grow this list when the number of available
    desktops changes.

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @return:        A list of virutal desktop names.
    @rtype:         util.PropertyCookie (UTF8_STRING[])
    """
    return util.PropertyCookie(
        util.get_property_unchecked(c, window,
                                    atom(c, '_NET_DESKTOP_NAMES')))

def set_desktop_names(c, window, desktop_names):
    """
    Sets the current list of desktop names.

    The names of all virtual desktops. This is a list of NULL-terminated
    strings in UTF-8 encoding [UTF8]. This property MAY be changed by a
    Pager or the Window Manager at any time.

    Note: The number of names could be different from
    _NET_NUMBER_OF_DESKTOPS. If it is less than _NET_NUMBER_OF_DESKTOPS,
    then the desktops with high numbers are unnamed. If it is larger than
    _NET_NUMBER_OF_DESKTOPS, then the excess names outside of the
    _NET_NUMBER_OF_DESKTOPS are considered to be reserved in case the
    number of desktops is increased.

    Rationale: The name is not a necessary attribute of a virtual desktop.
    Thus the availability or unavailability of names has no impact on
    virtual desktop functionality. Since names are set by users and users
    are likely to preset names for a fixed number of desktops, it doesn't
    make sense to shrink or grow this list when the number of available
    desktops changes.

    @param c:               An xpyb connection object.
    @param window:          A window identifier.
    @param desktop_names:   A list of new desktop names.
    @type desktop_names:    UTF8_STRING[]
    @rtype:                 xcb.VoidCookie
    """
    # Null terminate the list of desktop names
    nullterm = ''
    for desktop_name in desktop_names:
        nullterm += desktop_name + chr(0)

    return c.core.ChangeProperty(xcb.xproto.PropMode.Replace, window,
                                 atom(c, '_NET_DESKTOP_NAMES'),
                                 atom(c, 'UTF8_STRING'), 8,
                                 len(nullterm),
                                 nullterm)

def set_desktop_names_checked(c, window, desktop_names):
    """
    Sets the current list of desktop names.

    The names of all virtual desktops. This is a list of NULL-terminated
    strings in UTF-8 encoding [UTF8]. This property MAY be changed by a
    Pager or the Window Manager at any time.

    Note: The number of names could be different from
    _NET_NUMBER_OF_DESKTOPS. If it is less than _NET_NUMBER_OF_DESKTOPS,
    then the desktops with high numbers are unnamed. If it is larger than
    _NET_NUMBER_OF_DESKTOPS, then the excess names outside of the
    _NET_NUMBER_OF_DESKTOPS are considered to be reserved in case the
    number of desktops is increased.

    Rationale: The name is not a necessary attribute of a virtual desktop.
    Thus the availability or unavailability of names has no impact on
    virtual desktop functionality. Since names are set by users and users
    are likely to preset names for a fixed number of desktops, it doesn't
    make sense to shrink or grow this list when the number of available
    desktops changes.

    @param c:               An xpyb connection object.
    @param window:          A window identifier.
    @param desktop_names:   A list of new desktop names.
    @type desktop_names:    UTF8_STRING[]
    @rtype:                 xcb.VoidCookie
    """
    # Null terminate the list of desktop names
    nullterm = ''
    for desktop_name in desktop_names:
        nullterm += desktop_name + chr(0)

    return c.core.ChangePropertyChecked(xcb.xproto.PropMode.Replace, window,
                                 atom(c, '_NET_DESKTOP_NAMES'),
                                 atom(c, 'UTF8_STRING'), 8,
                                 len(nullterm),
                                 nullterm)

# _NET_ACTIVE_WINDOW

def get_active_window(c, window):
    """
    Returns the identifier of the currently active window.

    The window ID of the currently active window or None if no window has
    the focus. This is a read-only property set by the Window Manager.

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @return:        The window ID of the active window.
    @rtype:         util.PropertyCookieSingle (WINDOW/32)
    """
    return util.PropertyCookieSingle(
        util.get_property(c, window, atom(c, '_NET_ACTIVE_WINDOW')))

def get_active_window_unchecked(c, window):
    """
    Returns the identifier of the currently active window.

    The window ID of the currently active window or None if no window has
    the focus. This is a read-only property set by the Window Manager.

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @return:        The window ID of the active window.
    @rtype:         util.PropertyCookieSingle (WINDOW/32)
    """
    return util.PropertyCookieSingle(
        util.get_property_unchecked(c, window,
                                    atom(c, '_NET_ACTIVE_WINDOW')))

def set_active_window(c, window, active):
    """
    Sets the identifier of the currently active window.

    The window ID of the currently active window or None if no window has
    the focus. This is a read-only property set by the Window Manager.

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @param active:  The identifier of the window that is active.
    @type active:   WINDOW/32
    @rtype:         xcb.VoidCookie
    """
    packed = struct.pack('I', active)
    return c.core.ChangeProperty(xcb.xproto.PropMode.Replace, window,
                                 atom(c, '_NET_ACTIVE_WINDOW'),
                                 xcb.xproto.Atom.WINDOW, 32,
                                 1,
                                 packed)

def set_active_window_checked(c, window, active):
    """
    Sets the identifier of the currently active window.

    The window ID of the currently active window or None if no window has
    the focus. This is a read-only property set by the Window Manager.

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @param active:  The identifier of the window that is active.
    @type active:   WINDOW/32
    @rtype:         xcb.VoidCookie
    """
    packed = struct.pack('I', active)
    return c.core.ChangePropertyChecked(xcb.xproto.PropMode.Replace, window,
                                 atom(c, '_NET_ACTIVE_WINDOW'),
                                 xcb.xproto.Atom.WINDOW, 32,
                                 1,
                                 packed)

def request_active_window(c, active, source=1,
                            timestamp=xcb.xproto.Time.CurrentTime,
                            current=0):
    """
    Sends event to root window to set the active window.

    The window ID of the currently active window or None if no window has
    the focus. This is a read-only property set by the Window Manager.

    @param c:           An xpyb connection object.
    @param active:      The window ID of the window to make active.
    @type active:       WINDOW/32
    @param source:      The source indication.
    @type timestamp:    Milliseconds
    @param current:     Client's active toplevel window
    @rtype:             xcb.VoidCookie
    """
    return revent(c, active, atom(c, '_NET_ACTIVE_WINDOW'),
                  [source, timestamp, current])

def request_active_window_checked(c, active, source=1,
                                  timestamp=xcb.xproto.Time.CurrentTime,
                                  current=0):
    """
    Sends event to root window to set the active window.

    The window ID of the currently active window or None if no window has
    the focus. This is a read-only property set by the Window Manager.

    @param c:           An xpyb connection object.
    @param active:      The window ID of the window to make active.
    @type active:       WINDOW/32
    @param source:      The source indication.
    @type timestamp:    Milliseconds
    @param current:     Client's active toplevel window
    @rtype:             xcb.VoidCookie
    """
    return revent_checked(c, active, atom(c, '_NET_ACTIVE_WINDOW'),
                  [source, timestamp, current])

# _NET_WORKAREA

class WorkareaCookie(util.PropertyCookie):
    def reply(self):
        v = util.PropertyCookie.reply(self)

        if not v:
            return None

        ret = []
        for i in xrange(0, len(v), 4):
            ret.append({
                'x': v[i],
                'y': v[i + 1],
                'width': v[i + 2],
                'height': v[i + 3]
            })

        return ret

def get_workarea(c, window):
    """
    Returns the x, y, width and height defining the desktop workarea.

    This property MUST be set by the Window Manager upon calculating the
    work area for each desktop. Contains a geometry for each desktop. These
    geometries are specified relative to the viewport on each desktop and
    specify an area that is completely contained within the viewport. Work
    area SHOULD be used by desktop applications to place desktop icons
    appropriately.

    The Window Manager SHOULD calculate this space by taking the current
    page minus space occupied by dock and panel windows, as indicated by
    the _NET_WM_STRUT or _NET_WM_STRUT_PARTIAL properties set on client
    windows.

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @return:        A list of workarea dictionaries.

                    Keys: x, y, width, height
    @rtype:         util.WorkareaCookie (CARDINAL[][4]/32)
    """
    return WorkareaCookie(
        util.get_property(c, window, atom(c, '_NET_WORKAREA')))

def get_workarea_unchecked(c, window):
    """
    Returns the identifier of the currently active window.

    The window ID of the currently active window or None if no window has
    the focus. This is a read-only property set by the Window Manager.

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @return:        The window ID of the active window.
    @rtype:         util.PropertyCookieSingle (WINDOW/32)
    """
    return util.PropertyCookieSingle(
        util.get_property_unchecked(c, window,
                                    atom(c, '_NET_ACTIVE_WINDOW')))

def set_workarea(c, window, active):
    """
    Sets the identifier of the currently active window.

    The window ID of the currently active window or None if no window has
    the focus. This is a read-only property set by the Window Manager.

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @param active:  The identifier of the window that is active.
    @type active:   WINDOW/32
    @rtype:         xcb.VoidCookie
    """
    packed = struct.pack('I', active)
    return c.core.ChangeProperty(xcb.xproto.PropMode.Replace, window,
                                 atom(c, '_NET_ACTIVE_WINDOW'),
                                 xcb.xproto.Atom.WINDOW, 32,
                                 1,
                                 packed)

def set_workarea_checked(c, window, active):
    """
    Sets the identifier of the currently active window.

    The window ID of the currently active window or None if no window has
    the focus. This is a read-only property set by the Window Manager.

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @param active:  The identifier of the window that is active.
    @type active:   WINDOW/32
    @rtype:         xcb.VoidCookie
    """
    packed = struct.pack('I', active)
    return c.core.ChangePropertyChecked(xcb.xproto.PropMode.Replace, window,
                                 atom(c, '_NET_ACTIVE_WINDOW'),
                                 xcb.xproto.Atom.WINDOW, 32,
                                 1,
                                 packed)

# _NET_WM_NAME

def get_wm_name(c, window):
    return util.PropertyCookie(
        util.get_property(c, window, atom(c, '_NET_WM_NAME')))

def get_wm_name_unchecked(c, window):
    return util.PropertyCookie(
        util.get_property_unchecked(c, window, atom(c, '_NET_WM_NAME')))

def set_wm_name(c, window, wm_name):
    return c.core.ChangeProperty(xcb.xproto.PropMode.Replace, window,
                                    atom(c, '_NET_WM_NAME'),
                                    atom(c, 'UTF8_STRING'), 8, len(wm_name),
                                    wm_name)

def set_wm_name_checked(c, window, wm_name):
    return c.core.ChangePropertyChecked(xcb.xproto.PropMode.Replace, window,
                                    atom(c, '_NET_WM_NAME'),
                                    atom(c, 'UTF8_STRING'), 8, len(wm_name),
                                    wm_name)

# _NET_WM_DESKTOP

def get_wm_desktop(c, window):
    return util.PropertyCookieSingle(
        util.get_property(c, window, atom(c, '_NET_WM_DESKTOP')))

def get_wm_desktop_unchecked(c, window):
    return util.PropertyCookieSingle(
        util.get_property_unchecked(c, window, atom(c, '_NET_WM_DESKTOP')))

def set_wm_desktop(c, window, desktop):
    return c.core.ChangeProperty(xcb.xproto.PropMode.Replace, window,
                                    atom(c, '_NET_WM_DESKTOP'),
                                    CARDINAL, 32, len(str(desktop)),
                                    [desktop])

def set_wm_desktop_checked(c, window, desktop):
    return c.core.ChangePropertyChecked(xcb.xproto.PropMode.Replace, window,
                                    atom(c, '_NET_WM_DESKTOP'),
                                    CARDINAL, 32, len(str(desktop)),
                                    [desktop])

def request_wm_desktop(c, window, desktop, source=1):
    return revent(c, window, atom(c, '_NET_WM_DESKTOP'), [desktop, source])

def request_wm_desktop_checked(c, window, desktop, source=1):
    return revent_checked(c, window, atom(c, '_NET_WM_DESKTOP'),
                          [desktop, source])
