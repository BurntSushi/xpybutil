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

class State:
    Remove = 0
    Add = 1
    Toggle = 2

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

# _NET_VISIBLE_DESKTOPS

def get_visible_desktops(c, window):
    """
    Returns a list of visible desktops.

    The first desktop is on Xinerama screen 0, the second is on Xinerama
    screen 1, etc.

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @return:        A list of visible desktops.
    @rtype:         util.PropertyCookie (ATOM[]/32)
    """
    return util.PropertyCookie(
        util.get_property(c, window, atom(c, '_NET_VISIBLE_DESKTOPS')))

def get_visible_desktops_unchecked(c, window):
    """
    Returns a list of visible desktops.

    The first desktop is on Xinerama screen 0, the second is on Xinerama
    screen 1, etc.

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @return:        A list of visible desktops.
    @rtype:         util.PropertyCookie (ATOM[]/32)
    """
    return util.PropertyCookie(
        util.get_property_unchecked(c, window, 
                                    atom(c, '_NET_VISIBLE_DESKTOPS')))

def set_visible_desktops(c, window, desktops):
    """
    Sets the list of visible desktops.

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @param windows: A list of desktops.
    @type windows:  ATOM[]/32
    @rtype:         xcb.VoidCookie
    """
    packed = struct.pack('I' * len(desktops), *desktops)
    return c.core.ChangeProperty(xcb.xproto.PropMode.Replace, window,
                                 atom(c, '_NET_VISIBLE_DESKTOPS'),
                                 xcb.xproto.Atom.WINDOW, 32, len(desktops),
                                 packed)

def set_visible_desktops_checked(c, window, desktops):
    """
    Sets the list of visible desktops.

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @param windows: A list of desktops.
    @type windows:  ATOM[]/32
    @rtype:         xcb.VoidCookie
    """
    packed = struct.pack('I' * len(desktops), *desktops)
    return c.core.ChangePropertyChecked(xcb.xproto.PropMode.Replace, window,
                                 atom(c, '_NET_VISIBLE_DESKTOPS'),
                                 xcb.xproto.Atom.WINDOW, 32, len(desktops),
                                 packed)

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
        util.get_property_unchecked(c, window, atom(c, '_NET_WORKAREA')))

def set_workarea(c, window, workareas):
    """
    Sets the workarea (x, y, width, height) for each desktop.

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

    @param c:           An xpyb connection object.
    @param window:      A window identifier.
    @param workareas:   A list of x,y,width,height dictionaries.
    @type workareas:    CARDINAL[][4]/32
    @rtype:             xcb.VoidCookie
    """
    flatten = []
    for workarea in workareas:
        flatten.append(workarea['x'])
        flatten.append(workarea['y'])
        flatten.append(workarea['width'])
        flatten.append(workarea['height'])
    packed = struct.pack('I' * len(flatten), *flatten)

    return c.core.ChangeProperty(xcb.xproto.PropMode.Replace, window,
                                 atom(c, '_NET_WORKAREA'),
                                 CARDINAL, 32,
                                 len(flatten),
                                 packed)

def set_workarea_checked(c, window, workareas):
    """
    Sets the workarea (x, y, width, height) for each desktop.

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

    @param c:           An xpyb connection object.
    @param window:      A window identifier.
    @param workareas:   A list of x,y,width,height dictionaries.
    @type workareas:    CARDINAL[][4]/32
    @rtype:             xcb.VoidCookie
    """
    flatten = []
    for workarea in workareas:
        flatten.append(workarea['x'])
        flatten.append(workarea['y'])
        flatten.append(workarea['width'])
        flatten.append(workarea['height'])
    packed = struct.pack('I' * len(flatten), *flatten)

    return c.core.ChangePropertyChecked(xcb.xproto.PropMode.Replace, window,
                                 atom(c, '_NET_WORKAREA'),
                                 CARDINAL, 32,
                                 len(flatten),
                                 packed)

# _NET_SUPPORTING_WM_CHECK

def get_supporting_wm_check(c, window):
    """
    Returns the identifier of the child window created by the window manager.

    The Window Manager MUST set this property on the root window to be the
    ID of a child window created by himself, to indicate that a compliant
    window manager is active. The child window MUST also have the
    _NET_SUPPORTING_WM_CHECK property set to the ID of the child window.
    The child window MUST also have the _NET_WM_NAME property set to the
    name of the Window Manager.

    Rationale: The child window is used to distinguish an active Window
    Manager from a stale _NET_SUPPORTING_WM_CHECK property that happens to
    point to another window. If the _NET_SUPPORTING_WM_CHECK window on the
    client window is missing or not properly set, clients SHOULD assume
    that no conforming Window Manager is present.

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @return:        The window ID of the child window.
    @rtype:         util.PropertyCookieSingle (WINDOW/32)
    """
    return util.PropertyCookieSingle(
        util.get_property(c, window, atom(c, '_NET_SUPPORTING_WM_CHECK')))

def get_supporting_wm_check_unchecked(c, window):
    """
    Returns the identifier of the child window created by the window manager.

    The Window Manager MUST set this property on the root window to be the
    ID of a child window created by himself, to indicate that a compliant
    window manager is active. The child window MUST also have the
    _NET_SUPPORTING_WM_CHECK property set to the ID of the child window.
    The child window MUST also have the _NET_WM_NAME property set to the
    name of the Window Manager.

    Rationale: The child window is used to distinguish an active Window
    Manager from a stale _NET_SUPPORTING_WM_CHECK property that happens to
    point to another window. If the _NET_SUPPORTING_WM_CHECK window on the
    client window is missing or not properly set, clients SHOULD assume
    that no conforming Window Manager is present.

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @return:        The window ID of the child window.
    @rtype:         util.PropertyCookieSingle (WINDOW/32)
    """
    return util.PropertyCookieSingle(
        util.get_property_unchecked(c, window,
                                    atom(c, '_NET_SUPPORTING_WM_CHECK')))

def set_supporting_wm_check(c, window, child):
    """
    Sets the identifier of the child window created by the window manager.

    The Window Manager MUST set this property on the root window to be the
    ID of a child window created by himself, to indicate that a compliant
    window manager is active. The child window MUST also have the
    _NET_SUPPORTING_WM_CHECK property set to the ID of the child window.
    The child window MUST also have the _NET_WM_NAME property set to the
    name of the Window Manager.

    Rationale: The child window is used to distinguish an active Window
    Manager from a stale _NET_SUPPORTING_WM_CHECK property that happens to
    point to another window. If the _NET_SUPPORTING_WM_CHECK window on the
    client window is missing or not properly set, clients SHOULD assume
    that no conforming Window Manager is present.

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @param child:   The identifier of the child window.
    @type child:    WINDOW/32
    @rtype:         xcb.VoidCookie
    """
    packed = struct.pack('I', child)
    return c.core.ChangeProperty(xcb.xproto.PropMode.Replace, window,
                                 atom(c, '_NET_SUPPORTING_WM_CHECK'),
                                 xcb.xproto.Atom.WINDOW, 32,
                                 1,
                                 packed)

def set_supporting_wm_check_checked(c, window, child):
    """
    Sets the identifier of the child window created by the window manager.

    The Window Manager MUST set this property on the root window to be the
    ID of a child window created by himself, to indicate that a compliant
    window manager is active. The child window MUST also have the
    _NET_SUPPORTING_WM_CHECK property set to the ID of the child window.
    The child window MUST also have the _NET_WM_NAME property set to the
    name of the Window Manager.

    Rationale: The child window is used to distinguish an active Window
    Manager from a stale _NET_SUPPORTING_WM_CHECK property that happens to
    point to another window. If the _NET_SUPPORTING_WM_CHECK window on the
    client window is missing or not properly set, clients SHOULD assume
    that no conforming Window Manager is present.

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @param child:   The identifier of the child window.
    @type child:    WINDOW/32
    @rtype:         xcb.VoidCookie
    """
    packed = struct.pack('I', child)
    return c.core.ChangePropertyChecked(xcb.xproto.PropMode.Replace, window,
                                 atom(c, '_NET_SUPPORTING_WM_CHECK'),
                                 xcb.xproto.Atom.WINDOW, 32,
                                 1,
                                 packed)

# _NET_VIRTUAL_ROOTS

def get_virtual_roots(c, window):
    """
    Returns a list of identifiers for the virtual root windows.

    To implement virtual desktops, some Window Managers reparent client
    windows to a child of the root window. Window Managers using this
    technique MUST set this property to a list of IDs for windows that are
    acting as virtual root windows. This property allows background setting
    programs to work with virtual roots and allows clients to figure out
    the window manager frame windows of their windows.

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @return:        A list of window identifiers for the virtual root windows.
    @rtype:         util.PropertyCookie (WINDOW[]/32)
    """
    return util.PropertyCookie(
        util.get_property(c, window, atom(c, '_NET_VIRTUAL_ROOTS')))

def get_virtual_roots_unchecked(c, window):
    """
    Returns a list of identifiers for the virtual root windows.

    To implement virtual desktops, some Window Managers reparent client
    windows to a child of the root window. Window Managers using this
    technique MUST set this property to a list of IDs for windows that are
    acting as virtual root windows. This property allows background setting
    programs to work with virtual roots and allows clients to figure out
    the window manager frame windows of their windows.

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @return:        A list of window identifiers for the virtual root windows.
    @rtype:         util.PropertyCookie (WINDOW[]/32)
    """
    return util.PropertyCookie(
        util.get_property_unchecked(c, window,
                                    atom(c, '_NET_VIRTUAL_ROOTS')))

def set_virtual_roots(c, window, vroots):
    """
    Sets the identifiers of the virtual root windows.

    To implement virtual desktops, some Window Managers reparent client
    windows to a child of the root window. Window Managers using this
    technique MUST set this property to a list of IDs for windows that are
    acting as virtual root windows. This property allows background setting
    programs to work with virtual roots and allows clients to figure out
    the window manager frame windows of their windows.

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @param vroots:  A list of window identifiers for the virtual root windows.
    @type vroots:   WINDOW[]/32
    @rtype:         xcb.VoidCookie
    """
    packed = struct.pack('I' * len(vroots), *vroots)
    return c.core.ChangeProperty(xcb.xproto.PropMode.Replace, window,
                                 atom(c, '_NET_VIRTUAL_ROOTS'),
                                 xcb.xproto.Atom.WINDOW, 32,
                                 len(vroots),
                                 packed)

def set_virtual_roots_checked(c, window, vroots):
    """
    Sets the identifiers of the virtual root windows.

    To implement virtual desktops, some Window Managers reparent client
    windows to a child of the root window. Window Managers using this
    technique MUST set this property to a list of IDs for windows that are
    acting as virtual root windows. This property allows background setting
    programs to work with virtual roots and allows clients to figure out
    the window manager frame windows of their windows.

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @param vroots:  A list of window identifiers for the virtual root windows.
    @type vroots:   WINDOW[]/32
    @rtype:         xcb.VoidCookie
    """
    packed = struct.pack('I' * len(vroots), *vroots)
    return c.core.ChangePropertyChecked(xcb.xproto.PropMode.Replace, window,
                                 atom(c, '_NET_VIRTUAL_ROOTS'),
                                 xcb.xproto.Atom.WINDOW, 32,
                                 len(vroots),
                                 packed)

# _NET_DESKTOP_LAYOUT

class DesktopLayoutCookie(util.PropertyCookie):
    def reply(self):
        v = util.PropertyCookie.reply(self)

        if not v:
            return None

        return {
            'orientation': v[0],
            'columns': v[1],
            'rows': v[2],
            'starting_corner': v[3] if len(v) > 3 else StartingCorner.TopLeft
        }

def get_desktop_layout(c, window):
    """
    Returns the desktop layout.

    This property is set by a Pager, not by the Window Manager. When
    setting this property, the Pager must own a manager selection (as
    defined in the ICCCM 2.8). The manager selection is called
    _NET_DESKTOP_LAYOUT_Sn where n is the screen number. The purpose of
    this property is to allow the Window Manager to know the desktop layout
    displayed by the Pager.

    _NET_DESKTOP_LAYOUT describes the layout of virtual desktops relative
    to each other. More specifically, it describes the layout used by the
    owner of the manager selection. The Window Manager may use this layout
    information or may choose to ignore it. The property contains four
    values: the Pager orientation, the number of desktops in the X
    direction, the number in the Y direction, and the starting corner of
    the layout, i.e. the corner containing the first desktop.

    Note: In order to inter-operate with Pagers implementing an earlier
    draft of this document, Window Managers should accept a
    _NET_DESKTOP_LAYOUT property of length 3 and use _NET_WM_TOPLEFT as the
    starting corner in this case.

    The virtual desktops are arranged in a rectangle with rows rows and
    columns columns. If rows times columns does not match the total number
    of desktops as specified by _NET_NUMBER_OF_DESKTOPS, the
    highest-numbered workspaces are assumed to be nonexistent. Either rows
    or columns (but not both) may be specified as 0 in which case its
    actual value will be derived from _NET_NUMBER_OF_DESKTOPS.

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @return:        A desktop layout dictionary.

                    Keys: orientation, columns, rows, starting_corner
    @rtype:         DesktopLayoutCookie (CARDINAL[4]/32)
    """
    return DesktopLayoutCookie(
        util.get_property(c, window, atom(c, '_NET_DESKTOP_LAYOUT')))

def get_desktop_layout_unchecked(c, window):
    """
    Returns the desktop layout.

    This property is set by a Pager, not by the Window Manager. When
    setting this property, the Pager must own a manager selection (as
    defined in the ICCCM 2.8). The manager selection is called
    _NET_DESKTOP_LAYOUT_Sn where n is the screen number. The purpose of
    this property is to allow the Window Manager to know the desktop layout
    displayed by the Pager.

    _NET_DESKTOP_LAYOUT describes the layout of virtual desktops relative
    to each other. More specifically, it describes the layout used by the
    owner of the manager selection. The Window Manager may use this layout
    information or may choose to ignore it. The property contains four
    values: the Pager orientation, the number of desktops in the X
    direction, the number in the Y direction, and the starting corner of
    the layout, i.e. the corner containing the first desktop.

    Note: In order to inter-operate with Pagers implementing an earlier
    draft of this document, Window Managers should accept a
    _NET_DESKTOP_LAYOUT property of length 3 and use _NET_WM_TOPLEFT as the
    starting corner in this case.

    The virtual desktops are arranged in a rectangle with rows rows and
    columns columns. If rows times columns does not match the total number
    of desktops as specified by _NET_NUMBER_OF_DESKTOPS, the
    highest-numbered workspaces are assumed to be nonexistent. Either rows
    or columns (but not both) may be specified as 0 in which case its
    actual value will be derived from _NET_NUMBER_OF_DESKTOPS.

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @return:        A desktop layout dictionary.

                    Keys: orientation, columns, rows, starting_corner
    @rtype:         DesktopLayoutCookie (CARDINAL[4]/32)
    """
    return DesktopLayoutCookie(
        util.get_property_unchecked(c, window, atom(c, '_NET_DESKTOP_LAYOUT')))

def set_desktop_layout(c, window, orientation, columns, rows,
                       starting_corner=StartingCorner.TopLeft):
    """
    Sets the desktop layout.

    This property is set by a Pager, not by the Window Manager. When
    setting this property, the Pager must own a manager selection (as
    defined in the ICCCM 2.8). The manager selection is called
    _NET_DESKTOP_LAYOUT_Sn where n is the screen number. The purpose of
    this property is to allow the Window Manager to know the desktop layout
    displayed by the Pager.

    _NET_DESKTOP_LAYOUT describes the layout of virtual desktops relative
    to each other. More specifically, it describes the layout used by the
    owner of the manager selection. The Window Manager may use this layout
    information or may choose to ignore it. The property contains four
    values: the Pager orientation, the number of desktops in the X
    direction, the number in the Y direction, and the starting corner of
    the layout, i.e. the corner containing the first desktop.

    Note: In order to inter-operate with Pagers implementing an earlier
    draft of this document, Window Managers should accept a
    _NET_DESKTOP_LAYOUT property of length 3 and use _NET_WM_TOPLEFT as the
    starting corner in this case.

    The virtual desktops are arranged in a rectangle with rows rows and
    columns columns. If rows times columns does not match the total number
    of desktops as specified by _NET_NUMBER_OF_DESKTOPS, the
    highest-numbered workspaces are assumed to be nonexistent. Either rows
    or columns (but not both) may be specified as 0 in which case its
    actual value will be derived from _NET_NUMBER_OF_DESKTOPS.

    @param c:                   An xpyb connection object.
    @param window:              A window identifier.
    @param orientation:         Horizontal or vertical orientation.
    @type orientation:          CARDINAL/32
    @param columns:             Number of columns.
    @type columns:              CARDINAL/32
    @param rows:                Number of rows.
    @type rows:                 CARDINAL/32
    @param starting_corner:     Top left, top right, bottom right, or bottom
                                left may be specified as a starting corner.
    @type starting_corner:      CARDINAL/32
    @rtype:                     xcb.VoidCookie
    """
    packed = struct.pack('IIII', orientation, columns, rows, starting_corner)
    return c.core.ChangeProperty(xcb.xproto.PropMode.Replace, window,
                                 atom(c, '_NET_DESKTOP_LAYOUT'),
                                 CARDINAL, 32, 4,
                                 packed)

def set_desktop_layout_checked(c, window, orientation, columns, rows,
                               starting_corner=StartingCorner.TopLeft):
    """
    Sets the desktop layout.

    This property is set by a Pager, not by the Window Manager. When
    setting this property, the Pager must own a manager selection (as
    defined in the ICCCM 2.8). The manager selection is called
    _NET_DESKTOP_LAYOUT_Sn where n is the screen number. The purpose of
    this property is to allow the Window Manager to know the desktop layout
    displayed by the Pager.

    _NET_DESKTOP_LAYOUT describes the layout of virtual desktops relative
    to each other. More specifically, it describes the layout used by the
    owner of the manager selection. The Window Manager may use this layout
    information or may choose to ignore it. The property contains four
    values: the Pager orientation, the number of desktops in the X
    direction, the number in the Y direction, and the starting corner of
    the layout, i.e. the corner containing the first desktop.

    Note: In order to inter-operate with Pagers implementing an earlier
    draft of this document, Window Managers should accept a
    _NET_DESKTOP_LAYOUT property of length 3 and use _NET_WM_TOPLEFT as the
    starting corner in this case.

    The virtual desktops are arranged in a rectangle with rows rows and
    columns columns. If rows times columns does not match the total number
    of desktops as specified by _NET_NUMBER_OF_DESKTOPS, the
    highest-numbered workspaces are assumed to be nonexistent. Either rows
    or columns (but not both) may be specified as 0 in which case its
    actual value will be derived from _NET_NUMBER_OF_DESKTOPS.

    @param c:                   An xpyb connection object.
    @param window:              A window identifier.
    @param orientation:         Horizontal or vertical orientation.
    @type orientation:          CARDINAL/32
    @param columns:             Number of columns.
    @type columns:              CARDINAL/32
    @param rows:                Number of rows.
    @type rows:                 CARDINAL/32
    @param starting_corner:     Top left, top right, bottom right, or bottom
                                left may be specified as a starting corner.
    @type starting_corner:      CARDINAL/32
    @rtype:                     xcb.VoidCookie
    """
    packed = struct.pack('IIII', orientation, columns, rows, starting_corner)
    return c.core.ChangePropertyChecked(xcb.xproto.PropMode.Replace, window,
                                 atom(c, '_NET_DESKTOP_LAYOUT'),
                                 CARDINAL, 32, 4,
                                 packed)

# _NET_SHOWING_DESKTOP

class ShowingDesktopCookie(util.PropertyCookieSingle):
    def reply(self):
        v = util.PropertyCookieSingle.reply(self)

        if v is None:
            return None

        if v == 1:
            return True
        return False

def get_showing_desktop(c, window):
    """
    Returns whether the window manager is in "showing the desktop" mode.

    Some Window Managers have a "showing the desktop" mode in which windows
    are hidden, and the desktop background is displayed and focused. If a
    Window Manager supports the _NET_SHOWING_DESKTOP hint, it MUST set it
    to a value of 1 when the Window Manager is in "showing the desktop"
    mode, and a value of zero if the Window Manager is not in this mode.

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @return:        Boolean whether the window manager is in "showing desktop"
                    mode or not.
    @rtype:         ShowingDesktopCookie (CARDINAL/32)
    """
    return ShowingDesktopCookie(
        util.get_property(c, window, atom(c, '_NET_SHOWING_DESKTOP')))

def get_showing_desktop_unchecked(c, window):
    """
    Returns whether the window manager is in "showing the desktop" mode.

    Some Window Managers have a "showing the desktop" mode in which windows
    are hidden, and the desktop background is displayed and focused. If a
    Window Manager supports the _NET_SHOWING_DESKTOP hint, it MUST set it
    to a value of 1 when the Window Manager is in "showing the desktop"
    mode, and a value of zero if the Window Manager is not in this mode.

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @return:        Boolean whether the window manager is in "showing desktop"
                    mode or not.
    @rtype:         ShowingDesktopCookie (CARDINAL/32)
    """
    return ShowingDesktopCookie(
        util.get_property_unchecked(c, window,
                                    atom(c, '_NET_SHOWING_DESKTOP')))

def set_showing_desktop(c, window, showing_desktop):
    """
    Sets whether the window is in "showing the desktop" mode.

    Some Window Managers have a "showing the desktop" mode in which windows
    are hidden, and the desktop background is displayed and focused. If a
    Window Manager supports the _NET_SHOWING_DESKTOP hint, it MUST set it
    to a value of 1 when the Window Manager is in "showing the desktop"
    mode, and a value of zero if the Window Manager is not in this mode.

    @param c:                An xpyb connection object.
    @param window:           A window identifier.
    @param showing_desktop:  Boolean whether the window manager is in "showing
                             desktop" mode or not.
    @type showing_desktop:   CARDINAL/32
    @rtype:                  xcb.VoidCookie
    """
    return c.core.ChangeProperty(xcb.xproto.PropMode.Replace, window,
                                 atom(c, '_NET_SHOWING_DESKTOP'),
                                 CARDINAL, 32, 1,
                                 [showing_desktop])

def set_showing_desktop_checked(c, window, showing_desktop):
    """
    Sets whether the window is in "showing the desktop" mode.

    Some Window Managers have a "showing the desktop" mode in which windows
    are hidden, and the desktop background is displayed and focused. If a
    Window Manager supports the _NET_SHOWING_DESKTOP hint, it MUST set it
    to a value of 1 when the Window Manager is in "showing the desktop"
    mode, and a value of zero if the Window Manager is not in this mode.

    @param c:                An xpyb connection object.
    @param window:           A window identifier.
    @param showing_desktop:  Boolean whether the window manager is in "showing
                             desktop" mode or not.
    @type showing_desktop:   CARDINAL/32
    @rtype:                  xcb.VoidCookie
    """
    return c.core.ChangePropertyChecked(xcb.xproto.PropMode.Replace, window,
                                 atom(c, '_NET_SHOWING_DESKTOP'),
                                 CARDINAL, 32, 1,
                                 [showing_desktop])

def request_showing_desktop(c, showing_desktop):
    """
    Sends event to root window to put window manager in "showing desktop" mode.

    Some Window Managers have a "showing the desktop" mode in which windows
    are hidden, and the desktop background is displayed and focused. If a
    Window Manager supports the _NET_SHOWING_DESKTOP hint, it MUST set it
    to a value of 1 when the Window Manager is in "showing the desktop"
    mode, and a value of zero if the Window Manager is not in this mode.

    @param c:                An xpyb connection object.
    @param showing_desktop:  Boolean whether the window manager is in "showing
                             desktop" mode or not.
    @type showing_desktop:   CARDINAL/32
    @rtype:                  xcb.VoidCookie
    """
    return revent(c, root(c), atom(c, '_NET_SHOWING_DESKTOP'),
                  [showing_desktop])

def request_showing_desktop_checked(c, showing_desktop):
    """
    Sends event to root window to put window manager in "showing desktop" mode.

    Some Window Managers have a "showing the desktop" mode in which windows
    are hidden, and the desktop background is displayed and focused. If a
    Window Manager supports the _NET_SHOWING_DESKTOP hint, it MUST set it
    to a value of 1 when the Window Manager is in "showing the desktop"
    mode, and a value of zero if the Window Manager is not in this mode.

    @param c:                An xpyb connection object.
    @param showing_desktop:  Boolean whether the window manager is in "showing
                             desktop" mode or not.
    @type showing_desktop:   CARDINAL/32
    @rtype:                  xcb.VoidCookie
    """
    return revent_checked(c, root(c), atom(c, '_NET_SHOWING_DESKTOP'),
                          [showing_desktop])

# _NET_CLOSE_WINDOW

def request_close_window(c, window, timestamp=xcb.xproto.Time.CurrentTime,
                         source=1):
    """
    Sends event to root window to close a window.

    Rationale: A Window Manager might be more clever than the usual method
    (send WM_DELETE message if the protocol is selected, XKillClient
    otherwise). It might introduce a timeout, for example. Instead of
    duplicating the code, the Window Manager can easily do the job.

    @param c:           An xpyb connection object.
    @param window:      A window identifier.
    @param source:      The source indication.
    @type timestamp:    Milliseconds
    @rtype:             xcb.VoidCookie
    """
    return revent(c, window, atom(c, '_NET_CLOSE_WINDOW'),
                  [timestamp, source])

def request_close_window_checked(c, window, timestamp=xcb.xproto.Time.CurrentTime,
                                 source=1):
    """
    Sends event to root window to close a window.

    Rationale: A Window Manager might be more clever than the usual method
    (send WM_DELETE message if the protocol is selected, XKillClient
    otherwise). It might introduce a timeout, for example. Instead of
    duplicating the code, the Window Manager can easily do the job.

    @param c:           An xpyb connection object.
    @param window:      A window identifier.
    @param source:      The source indication.
    @type timestamp:    Milliseconds
    @rtype:             xcb.VoidCookie
    """
    return revent_checked(c, window, atom(c, '_NET_CLOSE_WINDOW'),
                          [timestamp, source])

# _NET_MOVERESIZE_WINDOW

def request_moveresize_window(c, window, x=None, y=None, width=None,
                              height=None,
                              gravity=xcb.xproto.Gravity.BitForget, source=1):
    """
    Sends event to root window to move/resize a window.

    The low byte of data.l[0] contains the gravity to use; it may contain
    any value allowed for the WM_SIZE_HINTS.win_gravity property: NorthWest
    (1), North (2), NorthEast (3), West (4), Center (5), East (6),
    SouthWest (7), South (8), SouthEast (9) and Static (10). A gravity of 0
    indicates that the Window Manager should use the gravity specified in
    WM_SIZE_HINTS.win_gravity. The bits 8 to 11 indicate the presence of x,
    y, width and height. The bits 12 to 15 indicate the source (see the
    section called "Source indication in requests"), so 0001 indicates the
    application and 0010 indicates a Pager or a Taskbar. The remaining bits
    should be set to zero.

    Pagers wanting to move or resize a window may send a
    _NET_MOVERESIZE_WINDOW client message request to the root window
    instead of using a ConfigureRequest.

    Window Managers should treat a _NET_MOVERESIZE_WINDOW message exactly
    like a ConfigureRequest (in particular, adhering to the ICCCM rules
    about synthetic ConfigureNotify events), except that they should use
    the gravity specified in the message.

    Rationale: Using a _NET_MOVERESIZE_WINDOW message with StaticGravity
    allows Pagers to exactly position and resize a window including its
    decorations without knowing the size of the decorations.

    @param c:           An xpyb connection object.
    @param window:      A window identifier.
    @param x:           x coordinate
    @param y:           y coordinate
    @param width:       Width
    @param height:      Height
    @param gravity:     Should be one of NorthWest, North, NorthEast, West,
                        Center, East, SouthWest, South, SouthEast, and Static.
                        If set to 0, the window manager should use the default
                        gravity for the window.
    @param source:      The source indication.
    @rtype:             xcb.VoidCookie
    """
    flags = gravity
    flags |= source << 12
    if x is not None:
        flags |= 1 << 8
    if y is not None:
        flags |= 1 << 9
    if width is not None:
        flags |= 1 << 10
    if height is not None:
        flags |= 1 << 11

    return revent(c, window, atom(c, '_NET_MOVERESIZE_WINDOW'),
                  [flags, x, y, width, height])

def request_moveresize_window_checked(c, window, x=None, y=None, width=None,
                                      height=None,
                                      gravity=xcb.xproto.Gravity.BitForget,
                                      source=1):
    """
    Sends event to root window to move/resize a window.

    The low byte of data.l[0] contains the gravity to use; it may contain
    any value allowed for the WM_SIZE_HINTS.win_gravity property: NorthWest
    (1), North (2), NorthEast (3), West (4), Center (5), East (6),
    SouthWest (7), South (8), SouthEast (9) and Static (10). A gravity of 0
    indicates that the Window Manager should use the gravity specified in
    WM_SIZE_HINTS.win_gravity. The bits 8 to 11 indicate the presence of x,
    y, width and height. The bits 12 to 15 indicate the source (see the
    section called "Source indication in requests"), so 0001 indicates the
    application and 0010 indicates a Pager or a Taskbar. The remaining bits
    should be set to zero.

    Pagers wanting to move or resize a window may send a
    _NET_MOVERESIZE_WINDOW client message request to the root window
    instead of using a ConfigureRequest.

    Window Managers should treat a _NET_MOVERESIZE_WINDOW message exactly
    like a ConfigureRequest (in particular, adhering to the ICCCM rules
    about synthetic ConfigureNotify events), except that they should use
    the gravity specified in the message.

    Rationale: Using a _NET_MOVERESIZE_WINDOW message with StaticGravity
    allows Pagers to exactly position and resize a window including its
    decorations without knowing the size of the decorations.

    @param c:           An xpyb connection object.
    @param window:      A window identifier.
    @param x:           x coordinate
    @param y:           y coordinate
    @param width:       Width
    @param height:      Height
    @param gravity:     Should be one of NorthWest, North, NorthEast, West,
                        Center, East, SouthWest, South, SouthEast, and Static.
                        If set to 0, the window manager should use the default
                        gravity for the window.
    @param source:      The source indication.
    @rtype:             xcb.VoidCookie
    """
    flags = gravity
    flags |= source << 12
    if x is not None:
        flags |= 1 << 8
    if y is not None:
        flags |= 1 << 9
    if width is not None:
        flags |= 1 << 10
    if height is not None:
        flags |= 1 << 11

    return revent_checked(c, window, atom(c, '_NET_MOVERESIZE_WINDOW'),
                          [flags, x, y, width, height])

# _NET_WM_MOVERESIZE

def request_wm_moveresize(c, window, direction, x_root=0, y_root=0,
                          button=0, source=1):
    """
    Sends event to root window to initiate window movement or resizing.

    This message allows Clients to initiate window movement or resizing.
    They can define their own move and size "grips", whilst letting the
    Window Manager control the actual operation. This means that all
    moves/resizes can happen in a consistent manner as defined by the
    Window Manager. See the section called "Source indication in requests"
    for details on the source indication.

    When sending this message in response to a button press event, button
    SHOULD indicate the button which was pressed, x_root and y_root MUST
    indicate the position of the button press with respect to the root window
    and direction MUST indicate whether this is a move or resize event, and if
    it is a resize event, which edges of the window the size grip applies to.
    When sending this message in response to a key event, the direction MUST
    indicate whether this this is a move or resize event and the other fields
    are unused.

    The Client MUST release all grabs prior to sending such message (except
    for the _NET_WM_MOVERESIZE_CANCEL message).

    The Window Manager can use the button field to determine the events on
    which it terminates the operation initiated by the _NET_WM_MOVERESIZE
    message. Since there is a race condition between a client sending the
    _NET_WM_MOVERESIZE message and the user releasing the button, Window
    Managers are advised to offer some other means to terminate the
    operation, e.g. by pressing the ESC key. The special value
    _NET_WM_MOVERESIZE_CANCEL also allows clients to cancel the operation
    by sending such message if they detect the release themselves (clients
    should send it if they get the button release after sending the move
    resize message, indicating that the WM did not get a grab in time to
    get the release).

    @param c:           An xpyb connection object.
    @param window:      A window identifier.
    @param direction:   Whether it is moving or resizing, and if resizing,
                        the direction. Can be one of the following flags:

                        _NET_WM_MOVERESIZE_SIZE_TOPLEFT         = 0

                        _NET_WM_MOVERESIZE_SIZE_TOP             = 1

                        _NET_WM_MOVERESIZE_SIZE_TOPRIGHT        = 2

                        _NET_WM_MOVERESIZE_SIZE_RIGHT           = 3

                        _NET_WM_MOVERESIZE_SIZE_BOTTOMRIGHT     = 4

                        _NET_WM_MOVERESIZE_SIZE_BOTTOM          = 5

                        _NET_WM_MOVERESIZE_SIZE_BOTTOMLEFT      = 6

                        _NET_WM_MOVERESIZE_SIZE_LEFT            = 7

                        _NET_WM_MOVERESIZE_MOVE                 = 8

                        _NET_WM_MOVERESIZE_SIZE_KEYBOARD        = 9

                        _NET_WM_MOVERESIZE_MOVE_KEYBOARD        = 10

                        _NET_WM_MOVERESIZE_CANCEL               = 11
    @param x_root:      x coordinate of the pointer.
    @param y_root:      y coordinate of the pointer.
    @param button:      Which button was pressed, if a mouse button was used
                        to initiate this request.
    @param source:      The source indication.
    @rtype:             xcb.VoidCookie
    """
    return revent(c, window, atom(c, '_NET_WM_MOVERESIZE'),
                  [x_root, y_root, direction, button, source])

def request_wm_moveresize_checked(c, window, direction, x_root=0, y_root=0,
                                  button=0, source=1):
    """
    Sends event to root window to initiate window movement or resizing.

    This message allows Clients to initiate window movement or resizing.
    They can define their own move and size "grips", whilst letting the
    Window Manager control the actual operation. This means that all
    moves/resizes can happen in a consistent manner as defined by the
    Window Manager. See the section called "Source indication in requests"
    for details on the source indication.

    When sending this message in response to a button press event, button
    SHOULD indicate the button which was pressed, x_root and y_root MUST
    indicate the position of the button press with respect to the root window
    and direction MUST indicate whether this is a move or resize event, and if
    it is a resize event, which edges of the window the size grip applies to.
    When sending this message in response to a key event, the direction MUST
    indicate whether this this is a move or resize event and the other fields
    are unused.

    The Client MUST release all grabs prior to sending such message (except
    for the _NET_WM_MOVERESIZE_CANCEL message).

    The Window Manager can use the button field to determine the events on
    which it terminates the operation initiated by the _NET_WM_MOVERESIZE
    message. Since there is a race condition between a client sending the
    _NET_WM_MOVERESIZE message and the user releasing the button, Window
    Managers are advised to offer some other means to terminate the
    operation, e.g. by pressing the ESC key. The special value
    _NET_WM_MOVERESIZE_CANCEL also allows clients to cancel the operation
    by sending such message if they detect the release themselves (clients
    should send it if they get the button release after sending the move
    resize message, indicating that the WM did not get a grab in time to
    get the release).

    @param c:           An xpyb connection object.
    @param window:      A window identifier.
    @param direction:   Whether it is moving or resizing, and if resizing,
                        the direction. Can be one of the following flags:

                        _NET_WM_MOVERESIZE_SIZE_TOPLEFT         = 0

                        _NET_WM_MOVERESIZE_SIZE_TOP             = 1

                        _NET_WM_MOVERESIZE_SIZE_TOPRIGHT        = 2

                        _NET_WM_MOVERESIZE_SIZE_RIGHT           = 3

                        _NET_WM_MOVERESIZE_SIZE_BOTTOMRIGHT     = 4

                        _NET_WM_MOVERESIZE_SIZE_BOTTOM          = 5

                        _NET_WM_MOVERESIZE_SIZE_BOTTOMLEFT      = 6

                        _NET_WM_MOVERESIZE_SIZE_LEFT            = 7

                        _NET_WM_MOVERESIZE_MOVE                 = 8

                        _NET_WM_MOVERESIZE_SIZE_KEYBOARD        = 9

                        _NET_WM_MOVERESIZE_MOVE_KEYBOARD        = 10

                        _NET_WM_MOVERESIZE_CANCEL               = 11
    @param x_root:      x coordinate of the pointer.
    @param y_root:      y coordinate of the pointer.
    @param button:      Which button was pressed, if a mouse button was used
                        to initiate this request.
    @param source:      The source indication.
    @rtype:             xcb.VoidCookie
    """
    return revent_checked(c, window, atom(c, '_NET_WM_MOVERESIZE'),
                          [x_root, y_root, direction, button, source])

# _NET_RESTACK_WINDOW

def request_restack_window(c, window, stack_mode=xcb.xproto.StackMode.Above,
                           sibling=0, source=1):
    """
    Sends event to root window to restack a window.

    This request is similar to ConfigureRequest with CWSibling and
    CWStackMode flags. It should be used only by pagers, applications can
    use normal ConfigureRequests. The source indication field should be
    therefore set to 2, see the section called "Source indication in
    requests" for details.

    Rationale: A Window Manager may put restrictions on configure requests
    from applications, for example it may under some conditions refuse to
    raise a window. This request makes it clear it comes from a pager or
    similar tool, and therefore the Window Manager should always obey it.

    @param c:           An xpyb connection object.
    @param window:      A window identifier.
    @param stack_mode:  Stacking mode of window. Can be one of the following
                        flags: Above, Below, TopIf, BottomIf, Opposite
    @param sibling:     A sibling window identifier.
    @param source:      The source indication.
    @rtype:             xcb.VoidCookie
    """
    return revent(c, window, atom(c, '_NET_RESTACK_WINDOW'),
                  [source, sibling, stack_mode])

def request_restack_window_checked(c, window,
                                   stack_mode=xcb.xproto.StackMode.Above,
                                   sibling=0,
                                   source=2):
    """
    Sends event to root window to restack a window.

    This request is similar to ConfigureRequest with CWSibling and
    CWStackMode flags. It should be used only by pagers, applications can
    use normal ConfigureRequests. The source indication field should be
    therefore set to 2, see the section called "Source indication in
    requests" for details.

    Rationale: A Window Manager may put restrictions on configure requests
    from applications, for example it may under some conditions refuse to
    raise a window. This request makes it clear it comes from a pager or
    similar tool, and therefore the Window Manager should always obey it.

    @param c:           An xpyb connection object.
    @param window:      A window identifier.
    @param stack_mode:  Stacking mode of window. Can be one of the following
                        flags: Above, Below, TopIf, BottomIf, Opposite
    @param sibling:     A sibling window identifier.
    @param source:      The source indication.
    @rtype:             xcb.VoidCookie
    """
    return revent_checked(c, window, atom(c, '_NET_RESTACK_WINDOW'),
                          [source, sibling, stack_mode])

# _NET_REQUEST_FRAME_EXTENTS

def request_request_frame_extents(c, window):
    """
    Sends event to root window ask the WM to estimate the frame extents.

    A Client whose window has not yet been mapped can request of the Window
    Manager an estimate of the frame extents it will be given upon mapping.
    To retrieve such an estimate, the Client MUST send a
    _NET_REQUEST_FRAME_EXTENTS message to the root window. The Window
    Manager MUST respond by estimating the prospective frame extents and
    setting the window's _NET_FRAME_EXTENTS property accordingly. The
    Client MUST handle the resulting _NET_FRAME_EXTENTS PropertyNotify
    event. So that the Window Manager has a good basis for estimation, the
    Client MUST set any window properties it intends to set before sending
    this message. The Client MUST be able to cope with imperfect estimates.

    Rationale: A client cannot calculate the dimensions of its window's
    frame before the window is mapped, but some toolkits need this
    information. Asking the window manager for an estimate of the extents
    is a workable solution. The estimate may depend on the current theme,
    font sizes or other window properties. The client can track changes to
    the frame's dimensions by listening for _NET_FRAME_EXTENTS
    PropertyNotify events.

    @param c:           An xpyb connection object.
    @param window:      A window identifier.
    @rtype:             xcb.VoidCookie
    """
    return revent(c, window, atom(c, '_NET_REQUEST_FRAME_EXTENTS'), [])

def request_request_frame_extents_checked(c, window):
    """
    Sends event to root window ask the WM to estimate the frame extents.

    A Client whose window has not yet been mapped can request of the Window
    Manager an estimate of the frame extents it will be given upon mapping.
    To retrieve such an estimate, the Client MUST send a
    _NET_REQUEST_FRAME_EXTENTS message to the root window. The Window
    Manager MUST respond by estimating the prospective frame extents and
    setting the window's _NET_FRAME_EXTENTS property accordingly. The
    Client MUST handle the resulting _NET_FRAME_EXTENTS PropertyNotify
    event. So that the Window Manager has a good basis for estimation, the
    Client MUST set any window properties it intends to set before sending
    this message. The Client MUST be able to cope with imperfect estimates.

    Rationale: A client cannot calculate the dimensions of its window's
    frame before the window is mapped, but some toolkits need this
    information. Asking the window manager for an estimate of the extents
    is a workable solution. The estimate may depend on the current theme,
    font sizes or other window properties. The client can track changes to
    the frame's dimensions by listening for _NET_FRAME_EXTENTS
    PropertyNotify events.

    @param c:           An xpyb connection object.
    @param window:      A window identifier.
    @rtype:             xcb.VoidCookie
    """
    return revent_checked(c, window, atom(c, '_NET_REQUEST_FRAME_EXTENTS'), [])

# _NET_WM_NAME

def get_wm_name(c, window):
    """
    Get the title of a window.

    The Client SHOULD set this to the title of the window in UTF-8
    encoding. If set, the Window Manager should use this in preference to
    WM_NAME.

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @return:        The window's title.
    @rtype:         util.PropertyCookie (UTF8_STRING)
    """
    return util.PropertyCookie(
        util.get_property(c, window, atom(c, '_NET_WM_NAME')))

def get_wm_name_unchecked(c, window):
    """
    Get the title of a window.

    The Client SHOULD set this to the title of the window in UTF-8
    encoding. If set, the Window Manager should use this in preference to
    WM_NAME.

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @return:        The window's title.
    @rtype:         util.PropertyCookie (UTF8_STRING)
    """
    return util.PropertyCookie(
        util.get_property_unchecked(c, window, atom(c, '_NET_WM_NAME')))

def set_wm_name(c, window, wm_name):
    """
    Sets the title of a window.

    The Client SHOULD set this to the title of the window in UTF-8
    encoding. If set, the Window Manager should use this in preference to
    WM_NAME.

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @param wm_name: The title of the window.
    @rtype:         xcb.VoidCookie
    """
    return c.core.ChangeProperty(xcb.xproto.PropMode.Replace, window,
                                    atom(c, '_NET_WM_NAME'),
                                    atom(c, 'UTF8_STRING'), 8, len(wm_name),
                                    wm_name)

def set_wm_name_checked(c, window, wm_name):
    """
    Sets the title of a window.

    The Client SHOULD set this to the title of the window in UTF-8
    encoding. If set, the Window Manager should use this in preference to
    WM_NAME.

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @param wm_name: The title of the window.
    @rtype:         xcb.VoidCookie
    """
    return c.core.ChangePropertyChecked(xcb.xproto.PropMode.Replace, window,
                                    atom(c, '_NET_WM_NAME'),
                                    atom(c, 'UTF8_STRING'), 8, len(wm_name),
                                    wm_name)

# _NET_WM_VISIBLE_NAME

def get_wm_visible_name(c, window):
    """
    Get the visible title of a window.

    If the Window Manager displays a window name other than _NET_WM_NAME
    the Window Manager MUST set this to the title displayed in UTF-8
    encoding.

    Rationale: This property is for Window Managers that display a title
    different from the _NET_WM_NAME or WM_NAME of the window (i.e. xterm
    <1>, xterm <2>, ... is shown, but _NET_WM_NAME / WM_NAME is still xterm
    for each window) thereby allowing Pagers to display the same title as
    the Window Manager.

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @return:        The window's visible title.
    @rtype:         util.PropertyCookie (UTF8_STRING)
    """
    return util.PropertyCookie(
        util.get_property(c, window, atom(c, '_NET_WM_VISIBLE_NAME')))

def get_wm_visible_name_unchecked(c, window):
    """
    Get the visible title of a window.

    If the Window Manager displays a window name other than _NET_WM_NAME
    the Window Manager MUST set this to the title displayed in UTF-8
    encoding.

    Rationale: This property is for Window Managers that display a title
    different from the _NET_WM_NAME or WM_NAME of the window (i.e. xterm
    <1>, xterm <2>, ... is shown, but _NET_WM_NAME / WM_NAME is still xterm
    for each window) thereby allowing Pagers to display the same title as
    the Window Manager.

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @return:        The window's visible title.
    @rtype:         util.PropertyCookie (UTF8_STRING)
    """
    return util.PropertyCookie(
        util.get_property_unchecked(c, window,
                                    atom(c, '_NET_WM_VISIBLE_NAME')))

def set_wm_visible_name(c, window, wm_name):
    """
    Sets the visible title of a window.

    If the Window Manager displays a window name other than _NET_WM_NAME
    the Window Manager MUST set this to the title displayed in UTF-8
    encoding.

    Rationale: This property is for Window Managers that display a title
    different from the _NET_WM_NAME or WM_NAME of the window (i.e. xterm
    <1>, xterm <2>, ... is shown, but _NET_WM_NAME / WM_NAME is still xterm
    for each window) thereby allowing Pagers to display the same title as
    the Window Manager.

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @param wm_name: The title of the window.
    @rtype:         xcb.VoidCookie
    """
    return c.core.ChangeProperty(xcb.xproto.PropMode.Replace, window,
                                    atom(c, '_NET_WM_VISIBLE_NAME'),
                                    atom(c, 'UTF8_STRING'), 8, len(wm_name),
                                    wm_name)

def set_wm_visible_name_checked(c, window, wm_name):
    """
    Sets the visible title of a window.

    If the Window Manager displays a window name other than _NET_WM_NAME
    the Window Manager MUST set this to the title displayed in UTF-8
    encoding.

    Rationale: This property is for Window Managers that display a title
    different from the _NET_WM_NAME or WM_NAME of the window (i.e. xterm
    <1>, xterm <2>, ... is shown, but _NET_WM_NAME / WM_NAME is still xterm
    for each window) thereby allowing Pagers to display the same title as
    the Window Manager.

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @param wm_name: The title of the window.
    @rtype:         xcb.VoidCookie
    """
    return c.core.ChangePropertyChecked(xcb.xproto.PropMode.Replace, window,
                                    atom(c, '_NET_WM_VISIBLE_NAME'),
                                    atom(c, 'UTF8_STRING'), 8, len(wm_name),
                                    wm_name)

# _NET_WM_ICON_NAME

def get_wm_icon_name(c, window):
    """
    Get the icon name of a window.

    The Client SHOULD set this to the title of the icon for this window in
    UTF-8 encoding. If set, the Window Manager should use this in
    preference to WM_ICON_NAME.

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @return:        The window's icon name.
    @rtype:         util.PropertyCookie (UTF8_STRING)
    """
    return util.PropertyCookie(
        util.get_property(c, window, atom(c, '_NET_WM_ICON_NAME')))

def get_wm_icon_name_unchecked(c, window):
    """
    Get the icon name of a window.

    The Client SHOULD set this to the title of the icon for this window in
    UTF-8 encoding. If set, the Window Manager should use this in
    preference to WM_ICON_NAME.

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @return:        The window's icon name.
    @rtype:         util.PropertyCookie (UTF8_STRING)
    """
    return util.PropertyCookie(
        util.get_property_unchecked(c, window,
                                    atom(c, '_NET_WM_ICON_NAME')))

def set_wm_icon_name(c, window, icon_name):
    """
    Sets the icon name of a window.

    The Client SHOULD set this to the title of the icon for this window in
    UTF-8 encoding. If set, the Window Manager should use this in
    preference to WM_ICON_NAME.

    @param c:           An xpyb connection object.
    @param window:      A window identifier.
    @param icon_name:   The icon name of the window.
    @rtype:             xcb.VoidCookie
    """
    return c.core.ChangeProperty(xcb.xproto.PropMode.Replace, window,
                                    atom(c, '_NET_WM_ICON_NAME'),
                                    atom(c, 'UTF8_STRING'), 8, len(icon_name),
                                    icon_name)

def set_wm_icon_name_checked(c, window, icon_name):
    """
    Sets the icon name of a window.

    The Client SHOULD set this to the title of the icon for this window in
    UTF-8 encoding. If set, the Window Manager should use this in
    preference to WM_ICON_NAME.

    @param c:           An xpyb connection object.
    @param window:      A window identifier.
    @param icon_name:   The icon name of the window.
    @rtype:             xcb.VoidCookie
    """
    return c.core.ChangePropertyChecked(xcb.xproto.PropMode.Replace, window,
                                    atom(c, '_NET_WM_ICON_NAME'),
                                    atom(c, 'UTF8_STRING'), 8, len(icon_name),
                                    icon_name)

# _NET_WM_VISIBLE_ICON_NAME

def get_wm_visible_icon_name(c, window):
    """
    Get the visible icon name of a window.

    If the Window Manager displays an icon name other than
    _NET_WM_ICON_NAME the Window Manager MUST set this to the title
    displayed in UTF-8 encoding.

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @return:        The window's visible icon name.
    @rtype:         util.PropertyCookie (UTF8_STRING)
    """
    return util.PropertyCookie(
        util.get_property(c, window, atom(c, '_NET_WM_VISIBLE_ICON_NAME')))

def get_wm_visible_icon_name_unchecked(c, window):
    """
    Get the visible icon name of a window.

    If the Window Manager displays an icon name other than
    _NET_WM_ICON_NAME the Window Manager MUST set this to the title
    displayed in UTF-8 encoding.

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @return:        The window's visible icon name.
    @rtype:         util.PropertyCookie (UTF8_STRING)
    """
    return util.PropertyCookie(
        util.get_property_unchecked(c, window,
                                    atom(c, '_NET_WM_VISIBLE_ICON_NAME')))

def set_wm_visible_icon_name(c, window, icon_name):
    """
    Sets the visible icon name of a window.

    If the Window Manager displays an icon name other than
    _NET_WM_ICON_NAME the Window Manager MUST set this to the title
    displayed in UTF-8 encoding.

    @param c:           An xpyb connection object.
    @param window:      A window identifier.
    @param icon_name:   The icon name of the window.
    @rtype:             xcb.VoidCookie
    """
    return c.core.ChangeProperty(xcb.xproto.PropMode.Replace, window,
                                    atom(c, '_NET_WM_VISIBLE_ICON_NAME'),
                                    atom(c, 'UTF8_STRING'), 8, len(icon_name),
                                    icon_name)

def set_wm_visible_icon_name_checked(c, window, icon_name):
    """
    Sets the visible icon name of a window.

    If the Window Manager displays an icon name other than
    _NET_WM_ICON_NAME the Window Manager MUST set this to the title
    displayed in UTF-8 encoding.

    @param c:           An xpyb connection object.
    @param window:      A window identifier.
    @param icon_name:   The icon name of the window.
    @rtype:             xcb.VoidCookie
    """
    return c.core.ChangePropertyChecked(xcb.xproto.PropMode.Replace, window,
                                    atom(c, '_NET_WM_VISIBLE_ICON_NAME'),
                                    atom(c, 'UTF8_STRING'), 8, len(icon_name),
                                    icon_name)

# _NET_WM_DESKTOP

def get_wm_desktop(c, window):
    """
    Get the desktop index of the window.

    Cardinal to determine the desktop the window is in (or wants to be)
    starting with 0 for the first desktop. A Client MAY choose not to set
    this property, in which case the Window Manager SHOULD place it as it
    wishes. 0xFFFFFFFF indicates that the window SHOULD appear on all
    desktops.

    The Window Manager should honor _NET_WM_DESKTOP whenever a withdrawn
    window requests to be mapped.

    The Window Manager should remove the property whenever a window is
    withdrawn but it should leave the property in place when it is shutting
    down, e.g. in response to losing ownership of the WM_Sn manager
    selection.

    Rationale: Removing the property upon window withdrawal helps legacy
    applications which want to reuse withdrawn windows. Not removing the
    property upon shutdown allows the next Window Manager to restore
    windows to their previous desktops.

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @return:        The window's virtual desktop index.
    @rtype:         util.PropertyCookieSingle (CARDINAL/32)
    """
    return util.PropertyCookieSingle(
        util.get_property(c, window, atom(c, '_NET_WM_DESKTOP')))

def get_wm_desktop_unchecked(c, window):
    """
    Get the desktop index of the window.

    Cardinal to determine the desktop the window is in (or wants to be)
    starting with 0 for the first desktop. A Client MAY choose not to set
    this property, in which case the Window Manager SHOULD place it as it
    wishes. 0xFFFFFFFF indicates that the window SHOULD appear on all
    desktops.

    The Window Manager should honor _NET_WM_DESKTOP whenever a withdrawn
    window requests to be mapped.

    The Window Manager should remove the property whenever a window is
    withdrawn but it should leave the property in place when it is shutting
    down, e.g. in response to losing ownership of the WM_Sn manager
    selection.

    Rationale: Removing the property upon window withdrawal helps legacy
    applications which want to reuse withdrawn windows. Not removing the
    property upon shutdown allows the next Window Manager to restore
    windows to their previous desktops.

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @return:        The window's virtual desktop index.
    @rtype:         util.PropertyCookieSingle (CARDINAL/32)
    """
    return util.PropertyCookieSingle(
        util.get_property_unchecked(c, window, atom(c, '_NET_WM_DESKTOP')))

def set_wm_desktop(c, window, desktop):
    """
    Sets the desktop index of the window.

    Cardinal to determine the desktop the window is in (or wants to be)
    starting with 0 for the first desktop. A Client MAY choose not to set
    this property, in which case the Window Manager SHOULD place it as it
    wishes. 0xFFFFFFFF indicates that the window SHOULD appear on all
    desktops.

    The Window Manager should honor _NET_WM_DESKTOP whenever a withdrawn
    window requests to be mapped.

    The Window Manager should remove the property whenever a window is
    withdrawn but it should leave the property in place when it is shutting
    down, e.g. in response to losing ownership of the WM_Sn manager
    selection.

    Rationale: Removing the property upon window withdrawal helps legacy
    applications which want to reuse withdrawn windows. Not removing the
    property upon shutdown allows the next Window Manager to restore
    windows to their previous desktops.

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @param desktop: A desktop index.
    @type desktop:  CARDINAL/32
    @rtype:         xcb.VoidCookie
    """
    return c.core.ChangeProperty(xcb.xproto.PropMode.Replace, window,
                                    atom(c, '_NET_WM_DESKTOP'),
                                    CARDINAL, 32, 1,
                                    [desktop])

def set_wm_desktop_checked(c, window, desktop):
    """
    Sets the desktop index of the window.

    Cardinal to determine the desktop the window is in (or wants to be)
    starting with 0 for the first desktop. A Client MAY choose not to set
    this property, in which case the Window Manager SHOULD place it as it
    wishes. 0xFFFFFFFF indicates that the window SHOULD appear on all
    desktops.

    The Window Manager should honor _NET_WM_DESKTOP whenever a withdrawn
    window requests to be mapped.

    The Window Manager should remove the property whenever a window is
    withdrawn but it should leave the property in place when it is shutting
    down, e.g. in response to losing ownership of the WM_Sn manager
    selection.

    Rationale: Removing the property upon window withdrawal helps legacy
    applications which want to reuse withdrawn windows. Not removing the
    property upon shutdown allows the next Window Manager to restore
    windows to their previous desktops.

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @param desktop: A desktop index.
    @type desktop:  CARDINAL/32
    @rtype:         xcb.VoidCookie
    """
    return c.core.ChangePropertyChecked(xcb.xproto.PropMode.Replace, window,
                                    atom(c, '_NET_WM_DESKTOP'),
                                    CARDINAL, 32, 1,
                                    [desktop])

def request_wm_desktop(c, window, desktop, source=1):
    """
    Sends an event to root window to change the desktop of the window.

    Cardinal to determine the desktop the window is in (or wants to be)
    starting with 0 for the first desktop. A Client MAY choose not to set
    this property, in which case the Window Manager SHOULD place it as it
    wishes. 0xFFFFFFFF indicates that the window SHOULD appear on all
    desktops.

    The Window Manager should honor _NET_WM_DESKTOP whenever a withdrawn
    window requests to be mapped.

    The Window Manager should remove the property whenever a window is
    withdrawn but it should leave the property in place when it is shutting
    down, e.g. in response to losing ownership of the WM_Sn manager
    selection.

    Rationale: Removing the property upon window withdrawal helps legacy
    applications which want to reuse withdrawn windows. Not removing the
    property upon shutdown allows the next Window Manager to restore
    windows to their previous desktops.

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @param desktop: A desktop index.
    @type desktop:  CARDINAL/32
    @param source:  The source indication.
    @rtype:         xcb.VoidCookie
    """
    return revent(c, window, atom(c, '_NET_WM_DESKTOP'), [desktop, source])

def request_wm_desktop_checked(c, window, desktop, source=1):
    """
    Sends an event to root window to change the desktop of the window.

    Cardinal to determine the desktop the window is in (or wants to be)
    starting with 0 for the first desktop. A Client MAY choose not to set
    this property, in which case the Window Manager SHOULD place it as it
    wishes. 0xFFFFFFFF indicates that the window SHOULD appear on all
    desktops.

    The Window Manager should honor _NET_WM_DESKTOP whenever a withdrawn
    window requests to be mapped.

    The Window Manager should remove the property whenever a window is
    withdrawn but it should leave the property in place when it is shutting
    down, e.g. in response to losing ownership of the WM_Sn manager
    selection.

    Rationale: Removing the property upon window withdrawal helps legacy
    applications which want to reuse withdrawn windows. Not removing the
    property upon shutdown allows the next Window Manager to restore
    windows to their previous desktops.

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @param desktop: A desktop index.
    @type desktop:  CARDINAL/32
    @param source:  The source indication.
    @rtype:         xcb.VoidCookie
    """
    return revent_checked(c, window, atom(c, '_NET_WM_DESKTOP'),
                          [desktop, source])

# _NET_WM_WINDOW_TYPE

def get_wm_window_type(c, window):
    """
    Get a list of atoms representing the type of the window.

    This SHOULD be set by the Client before mapping to a list of atoms
    indicating the functional type of the window. This property SHOULD be
    used by the window manager in determining the decoration, stacking
    position and other behavior of the window. The Client SHOULD specify
    window types in order of preference (the first being most preferable)
    but MUST include at least one of the basic window type atoms from the
    list below. This is to allow for extension of the list of types whilst
    providing default behavior for Window Managers that do not recognize
    the extensions.

    This hint SHOULD also be set for override-redirect windows to allow
    compositing managers to apply consistent decorations to menus, tooltips
    etc.

    Rationale: This hint is intended to replace the MOTIF hints. One of the
    objections to the MOTIF hints is that they are a purely visual
    description of the window decoration. By describing the function of the
    window, the Window Manager can apply consistent decoration and behavior
    to windows of the same type. Possible examples of behavior include
    keeping dock/panels on top or allowing pinnable menus / toolbars to
    only be hidden when another window has focus (NextStep style).

    _NET_WM_WINDOW_TYPE_DESKTOP indicates a desktop feature. This can
    include a single window containing desktop icons with the same
    dimensions as the screen, allowing the desktop environment to have full
    control of the desktop, without the need for proxying root window clicks.

    _NET_WM_WINDOW_TYPE_DOCK indicates a dock or panel feature. Typically a
    Window Manager would keep such windows on top of all other windows.

    _NET_WM_WINDOW_TYPE_TOOLBAR and _NET_WM_WINDOW_TYPE_MENU indicate
    toolbar and pinnable menu windows, respectively (i.e. toolbars and
    menus "torn off" from the main application). Windows of this type may
    set the WM_TRANSIENT_FOR hint indicating the main application window.
    Note that the _NET_WM_WINDOW_TYPE_MENU should be set on torn-off
    managed windows, where _NET_WM_WINDOW_TYPE_DROPDOWN_MENU and
    _NET_WM_WINDOW_TYPE_POPUP_MENU are typically used on override-redirect
    windows.

    _NET_WM_WINDOW_TYPE_UTILITY indicates a small persistent utility
    window, such as a palette or toolbox. It is distinct from type TOOLBAR
    because it does not correspond to a toolbar torn off from the main
    application. It's distinct from type DIALOG because it isn't a
    transient dialog, the user will probably keep it open while they're
    working. Windows of this type may set the WM_TRANSIENT_FOR hint
    indicating the main application window.

    _NET_WM_WINDOW_TYPE_SPLASH indicates that the window is a splash screen
    displayed as an application is starting up.

    _NET_WM_WINDOW_TYPE_DIALOG indicates that this is a dialog window. If
    _NET_WM_WINDOW_TYPE is not set, then managed windows with
    WM_TRANSIENT_FOR set MUST be taken as this type. Override-redirect
    windows with WM_TRANSIENT_FOR, but without _NET_WM_WINDOW_TYPE must be
    taken as _NET_WM_WINDOW_TYPE_NORMAL.

    _NET_WM_WINDOW_TYPE_DROPDOWN_MENU indicates that the window in question
    is a dropdown menu, ie., the kind of menu that typically appears when
    the user clicks on a menubar, as opposed to a popup menu which
    typically appears when the user right-clicks on an object. This
    property is typically used on override-redirect windows.

    _NET_WM_WINDOW_TYPE_POPUP_MENU indicates that the window in question is
    a popup menu, ie., the kind of menu that typically appears when the
    user right clicks on an object, as opposed to a dropdown menu which
    typically appears when the user clicks on a menubar. This property is
    typically used on override-redirect windows.

    _NET_WM_WINDOW_TYPE_TOOLTIP indicates that the window in question is a
    tooltip, ie., a short piece of explanatory text that typically appear
    after the mouse cursor hovers over an object for a while. This property
    is typically used on override-redirect windows.

    _NET_WM_WINDOW_TYPE_NOTIFICATION indicates a notification. An example
    of a notification would be a bubble appearing with informative text
    such as "Your laptop is running out of power" etc. This property is
    typically used on override-redirect windows.

    _NET_WM_WINDOW_TYPE_COMBO should be used on the windows that are popped
    up by combo boxes. An example is a window that appears below a text
    field with a list of suggested completions. This property is typically
    used on override-redirect windows.

    _NET_WM_WINDOW_TYPE_DND indicates that the window is being dragged.
    Clients should set this hint when the window in question contains a
    representation of an object being dragged from one place to another. An
    example would be a window containing an icon that is being dragged from
    one file manager window to another. This property is typically used on
    override-redirect windows.

    _NET_WM_WINDOW_TYPE_NORMAL indicates that this is a normal, top-level
    window, either managed or override-redirect. Managed windows with
    neither _NET_WM_WINDOW_TYPE nor WM_TRANSIENT_FOR set MUST be taken as
    this type. Override-redirect windows without _NET_WM_WINDOW_TYPE, must
    be taken as this type, whether or not they have WM_TRANSIENT_FOR set.

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @return:        A list of atoms corresponding to this window's type.
    @rtype:         util.PropertyCookie (ATOM[]/32)
    """
    return util.PropertyCookie(
        util.get_property(c, window, atom(c, '_NET_WM_WINDOW_TYPE')))

def get_wm_window_type_unchecked(c, window):
    """
    Get a list of atoms representing the type of the window.

    This SHOULD be set by the Client before mapping to a list of atoms
    indicating the functional type of the window. This property SHOULD be
    used by the window manager in determining the decoration, stacking
    position and other behavior of the window. The Client SHOULD specify
    window types in order of preference (the first being most preferable)
    but MUST include at least one of the basic window type atoms from the
    list below. This is to allow for extension of the list of types whilst
    providing default behavior for Window Managers that do not recognize
    the extensions.

    This hint SHOULD also be set for override-redirect windows to allow
    compositing managers to apply consistent decorations to menus, tooltips
    etc.

    Rationale: This hint is intended to replace the MOTIF hints. One of the
    objections to the MOTIF hints is that they are a purely visual
    description of the window decoration. By describing the function of the
    window, the Window Manager can apply consistent decoration and behavior
    to windows of the same type. Possible examples of behavior include
    keeping dock/panels on top or allowing pinnable menus / toolbars to
    only be hidden when another window has focus (NextStep style).

    _NET_WM_WINDOW_TYPE_DESKTOP indicates a desktop feature. This can
    include a single window containing desktop icons with the same
    dimensions as the screen, allowing the desktop environment to have full
    control of the desktop, without the need for proxying root window clicks.

    _NET_WM_WINDOW_TYPE_DOCK indicates a dock or panel feature. Typically a
    Window Manager would keep such windows on top of all other windows.

    _NET_WM_WINDOW_TYPE_TOOLBAR and _NET_WM_WINDOW_TYPE_MENU indicate
    toolbar and pinnable menu windows, respectively (i.e. toolbars and
    menus "torn off" from the main application). Windows of this type may
    set the WM_TRANSIENT_FOR hint indicating the main application window.
    Note that the _NET_WM_WINDOW_TYPE_MENU should be set on torn-off
    managed windows, where _NET_WM_WINDOW_TYPE_DROPDOWN_MENU and
    _NET_WM_WINDOW_TYPE_POPUP_MENU are typically used on override-redirect
    windows.

    _NET_WM_WINDOW_TYPE_UTILITY indicates a small persistent utility
    window, such as a palette or toolbox. It is distinct from type TOOLBAR
    because it does not correspond to a toolbar torn off from the main
    application. It's distinct from type DIALOG because it isn't a
    transient dialog, the user will probably keep it open while they're
    working. Windows of this type may set the WM_TRANSIENT_FOR hint
    indicating the main application window.

    _NET_WM_WINDOW_TYPE_SPLASH indicates that the window is a splash screen
    displayed as an application is starting up.

    _NET_WM_WINDOW_TYPE_DIALOG indicates that this is a dialog window. If
    _NET_WM_WINDOW_TYPE is not set, then managed windows with
    WM_TRANSIENT_FOR set MUST be taken as this type. Override-redirect
    windows with WM_TRANSIENT_FOR, but without _NET_WM_WINDOW_TYPE must be
    taken as _NET_WM_WINDOW_TYPE_NORMAL.

    _NET_WM_WINDOW_TYPE_DROPDOWN_MENU indicates that the window in question
    is a dropdown menu, ie., the kind of menu that typically appears when
    the user clicks on a menubar, as opposed to a popup menu which
    typically appears when the user right-clicks on an object. This
    property is typically used on override-redirect windows.

    _NET_WM_WINDOW_TYPE_POPUP_MENU indicates that the window in question is
    a popup menu, ie., the kind of menu that typically appears when the
    user right clicks on an object, as opposed to a dropdown menu which
    typically appears when the user clicks on a menubar. This property is
    typically used on override-redirect windows.

    _NET_WM_WINDOW_TYPE_TOOLTIP indicates that the window in question is a
    tooltip, ie., a short piece of explanatory text that typically appear
    after the mouse cursor hovers over an object for a while. This property
    is typically used on override-redirect windows.

    _NET_WM_WINDOW_TYPE_NOTIFICATION indicates a notification. An example
    of a notification would be a bubble appearing with informative text
    such as "Your laptop is running out of power" etc. This property is
    typically used on override-redirect windows.

    _NET_WM_WINDOW_TYPE_COMBO should be used on the windows that are popped
    up by combo boxes. An example is a window that appears below a text
    field with a list of suggested completions. This property is typically
    used on override-redirect windows.

    _NET_WM_WINDOW_TYPE_DND indicates that the window is being dragged.
    Clients should set this hint when the window in question contains a
    representation of an object being dragged from one place to another. An
    example would be a window containing an icon that is being dragged from
    one file manager window to another. This property is typically used on
    override-redirect windows.

    _NET_WM_WINDOW_TYPE_NORMAL indicates that this is a normal, top-level
    window, either managed or override-redirect. Managed windows with
    neither _NET_WM_WINDOW_TYPE nor WM_TRANSIENT_FOR set MUST be taken as
    this type. Override-redirect windows without _NET_WM_WINDOW_TYPE, must
    be taken as this type, whether or not they have WM_TRANSIENT_FOR set.

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @return:        A list of atoms corresponding to this window's type.
    @rtype:         util.PropertyCookie (ATOM[]/32)
    """
    return util.PropertyCookie(
        util.get_property_unchecked(c, window, atom(c, '_NET_WM_WINDOW_TYPE')))

def set_wm_window_type(c, window, types):
    """
    Sets the list of atoms representing this window's type.

    This SHOULD be set by the Client before mapping to a list of atoms
    indicating the functional type of the window. This property SHOULD be
    used by the window manager in determining the decoration, stacking
    position and other behavior of the window. The Client SHOULD specify
    window types in order of preference (the first being most preferable)
    but MUST include at least one of the basic window type atoms from the
    list below. This is to allow for extension of the list of types whilst
    providing default behavior for Window Managers that do not recognize
    the extensions.

    This hint SHOULD also be set for override-redirect windows to allow
    compositing managers to apply consistent decorations to menus, tooltips
    etc.

    Rationale: This hint is intended to replace the MOTIF hints. One of the
    objections to the MOTIF hints is that they are a purely visual
    description of the window decoration. By describing the function of the
    window, the Window Manager can apply consistent decoration and behavior
    to windows of the same type. Possible examples of behavior include
    keeping dock/panels on top or allowing pinnable menus / toolbars to
    only be hidden when another window has focus (NextStep style).

    _NET_WM_WINDOW_TYPE_DESKTOP indicates a desktop feature. This can
    include a single window containing desktop icons with the same
    dimensions as the screen, allowing the desktop environment to have full
    control of the desktop, without the need for proxying root window clicks.

    _NET_WM_WINDOW_TYPE_DOCK indicates a dock or panel feature. Typically a
    Window Manager would keep such windows on top of all other windows.

    _NET_WM_WINDOW_TYPE_TOOLBAR and _NET_WM_WINDOW_TYPE_MENU indicate
    toolbar and pinnable menu windows, respectively (i.e. toolbars and
    menus "torn off" from the main application). Windows of this type may
    set the WM_TRANSIENT_FOR hint indicating the main application window.
    Note that the _NET_WM_WINDOW_TYPE_MENU should be set on torn-off
    managed windows, where _NET_WM_WINDOW_TYPE_DROPDOWN_MENU and
    _NET_WM_WINDOW_TYPE_POPUP_MENU are typically used on override-redirect
    windows.

    _NET_WM_WINDOW_TYPE_UTILITY indicates a small persistent utility
    window, such as a palette or toolbox. It is distinct from type TOOLBAR
    because it does not correspond to a toolbar torn off from the main
    application. It's distinct from type DIALOG because it isn't a
    transient dialog, the user will probably keep it open while they're
    working. Windows of this type may set the WM_TRANSIENT_FOR hint
    indicating the main application window.

    _NET_WM_WINDOW_TYPE_SPLASH indicates that the window is a splash screen
    displayed as an application is starting up.

    _NET_WM_WINDOW_TYPE_DIALOG indicates that this is a dialog window. If
    _NET_WM_WINDOW_TYPE is not set, then managed windows with
    WM_TRANSIENT_FOR set MUST be taken as this type. Override-redirect
    windows with WM_TRANSIENT_FOR, but without _NET_WM_WINDOW_TYPE must be
    taken as _NET_WM_WINDOW_TYPE_NORMAL.

    _NET_WM_WINDOW_TYPE_DROPDOWN_MENU indicates that the window in question
    is a dropdown menu, ie., the kind of menu that typically appears when
    the user clicks on a menubar, as opposed to a popup menu which
    typically appears when the user right-clicks on an object. This
    property is typically used on override-redirect windows.

    _NET_WM_WINDOW_TYPE_POPUP_MENU indicates that the window in question is
    a popup menu, ie., the kind of menu that typically appears when the
    user right clicks on an object, as opposed to a dropdown menu which
    typically appears when the user clicks on a menubar. This property is
    typically used on override-redirect windows.

    _NET_WM_WINDOW_TYPE_TOOLTIP indicates that the window in question is a
    tooltip, ie., a short piece of explanatory text that typically appear
    after the mouse cursor hovers over an object for a while. This property
    is typically used on override-redirect windows.

    _NET_WM_WINDOW_TYPE_NOTIFICATION indicates a notification. An example
    of a notification would be a bubble appearing with informative text
    such as "Your laptop is running out of power" etc. This property is
    typically used on override-redirect windows.

    _NET_WM_WINDOW_TYPE_COMBO should be used on the windows that are popped
    up by combo boxes. An example is a window that appears below a text
    field with a list of suggested completions. This property is typically
    used on override-redirect windows.

    _NET_WM_WINDOW_TYPE_DND indicates that the window is being dragged.
    Clients should set this hint when the window in question contains a
    representation of an object being dragged from one place to another. An
    example would be a window containing an icon that is being dragged from
    one file manager window to another. This property is typically used on
    override-redirect windows.

    _NET_WM_WINDOW_TYPE_NORMAL indicates that this is a normal, top-level
    window, either managed or override-redirect. Managed windows with
    neither _NET_WM_WINDOW_TYPE nor WM_TRANSIENT_FOR set MUST be taken as
    this type. Override-redirect windows without _NET_WM_WINDOW_TYPE, must
    be taken as this type, whether or not they have WM_TRANSIENT_FOR set.

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @param types:   A list of window type atoms.
    @type types:    ATOM[]/32
    @rtype:         xcb.VoidCookie
    """
    packed = struct.pack('I' * len(types), *types)
    return c.core.ChangeProperty(xcb.xproto.PropMode.Replace, window,
                                 atom(c, '_NET_WM_WINDOW_TYPE'),
                                 xcb.xproto.Atom.ATOM, 32, len(types),
                                 packed)

def set_wm_window_type_checked(c, window, types):
    """
    Sets the list of atoms representing this window's type.

    This SHOULD be set by the Client before mapping to a list of atoms
    indicating the functional type of the window. This property SHOULD be
    used by the window manager in determining the decoration, stacking
    position and other behavior of the window. The Client SHOULD specify
    window types in order of preference (the first being most preferable)
    but MUST include at least one of the basic window type atoms from the
    list below. This is to allow for extension of the list of types whilst
    providing default behavior for Window Managers that do not recognize
    the extensions.

    This hint SHOULD also be set for override-redirect windows to allow
    compositing managers to apply consistent decorations to menus, tooltips
    etc.

    Rationale: This hint is intended to replace the MOTIF hints. One of the
    objections to the MOTIF hints is that they are a purely visual
    description of the window decoration. By describing the function of the
    window, the Window Manager can apply consistent decoration and behavior
    to windows of the same type. Possible examples of behavior include
    keeping dock/panels on top or allowing pinnable menus / toolbars to
    only be hidden when another window has focus (NextStep style).

    _NET_WM_WINDOW_TYPE_DESKTOP indicates a desktop feature. This can
    include a single window containing desktop icons with the same
    dimensions as the screen, allowing the desktop environment to have full
    control of the desktop, without the need for proxying root window clicks.

    _NET_WM_WINDOW_TYPE_DOCK indicates a dock or panel feature. Typically a
    Window Manager would keep such windows on top of all other windows.

    _NET_WM_WINDOW_TYPE_TOOLBAR and _NET_WM_WINDOW_TYPE_MENU indicate
    toolbar and pinnable menu windows, respectively (i.e. toolbars and
    menus "torn off" from the main application). Windows of this type may
    set the WM_TRANSIENT_FOR hint indicating the main application window.
    Note that the _NET_WM_WINDOW_TYPE_MENU should be set on torn-off
    managed windows, where _NET_WM_WINDOW_TYPE_DROPDOWN_MENU and
    _NET_WM_WINDOW_TYPE_POPUP_MENU are typically used on override-redirect
    windows.

    _NET_WM_WINDOW_TYPE_UTILITY indicates a small persistent utility
    window, such as a palette or toolbox. It is distinct from type TOOLBAR
    because it does not correspond to a toolbar torn off from the main
    application. It's distinct from type DIALOG because it isn't a
    transient dialog, the user will probably keep it open while they're
    working. Windows of this type may set the WM_TRANSIENT_FOR hint
    indicating the main application window.

    _NET_WM_WINDOW_TYPE_SPLASH indicates that the window is a splash screen
    displayed as an application is starting up.

    _NET_WM_WINDOW_TYPE_DIALOG indicates that this is a dialog window. If
    _NET_WM_WINDOW_TYPE is not set, then managed windows with
    WM_TRANSIENT_FOR set MUST be taken as this type. Override-redirect
    windows with WM_TRANSIENT_FOR, but without _NET_WM_WINDOW_TYPE must be
    taken as _NET_WM_WINDOW_TYPE_NORMAL.

    _NET_WM_WINDOW_TYPE_DROPDOWN_MENU indicates that the window in question
    is a dropdown menu, ie., the kind of menu that typically appears when
    the user clicks on a menubar, as opposed to a popup menu which
    typically appears when the user right-clicks on an object. This
    property is typically used on override-redirect windows.

    _NET_WM_WINDOW_TYPE_POPUP_MENU indicates that the window in question is
    a popup menu, ie., the kind of menu that typically appears when the
    user right clicks on an object, as opposed to a dropdown menu which
    typically appears when the user clicks on a menubar. This property is
    typically used on override-redirect windows.

    _NET_WM_WINDOW_TYPE_TOOLTIP indicates that the window in question is a
    tooltip, ie., a short piece of explanatory text that typically appear
    after the mouse cursor hovers over an object for a while. This property
    is typically used on override-redirect windows.

    _NET_WM_WINDOW_TYPE_NOTIFICATION indicates a notification. An example
    of a notification would be a bubble appearing with informative text
    such as "Your laptop is running out of power" etc. This property is
    typically used on override-redirect windows.

    _NET_WM_WINDOW_TYPE_COMBO should be used on the windows that are popped
    up by combo boxes. An example is a window that appears below a text
    field with a list of suggested completions. This property is typically
    used on override-redirect windows.

    _NET_WM_WINDOW_TYPE_DND indicates that the window is being dragged.
    Clients should set this hint when the window in question contains a
    representation of an object being dragged from one place to another. An
    example would be a window containing an icon that is being dragged from
    one file manager window to another. This property is typically used on
    override-redirect windows.

    _NET_WM_WINDOW_TYPE_NORMAL indicates that this is a normal, top-level
    window, either managed or override-redirect. Managed windows with
    neither _NET_WM_WINDOW_TYPE nor WM_TRANSIENT_FOR set MUST be taken as
    this type. Override-redirect windows without _NET_WM_WINDOW_TYPE, must
    be taken as this type, whether or not they have WM_TRANSIENT_FOR set.

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @param types:   A list of window type atoms.
    @type types:    ATOM[]/32
    @rtype:         xcb.VoidCookie
    """
    packed = struct.pack('I' * len(types), *types)
    return c.core.ChangePropertyChecked(xcb.xproto.PropMode.Replace, window,
                                        atom(c, '_NET_WM_WINDOW_TYPE'),
                                        xcb.xproto.Atom.ATOM, 32, len(types),
                                        packed)

# _NET_WM_STATE

def get_wm_state(c, window):
    """
    Get a list of atoms representing the state of the window.

    A list of hints describing the window state. Atoms present in the list
    MUST be considered set, atoms not present in the list MUST be
    considered not set. The Window Manager SHOULD honor _NET_WM_STATE
    whenever a withdrawn window requests to be mapped. A Client wishing to
    change the state of a window MUST send a _NET_WM_STATE client message
    to the root window (see below). The Window Manager MUST keep this
    property updated to reflect the current state of the window.

    The Window Manager should remove the property whenever a window is
    withdrawn, but it should leave the property in place when it is
    shutting down, e.g. in response to losing ownership of the WM_Sn
    manager selection.

    Rationale: Removing the property upon window withdrawal helps legacy
    applications which want to reuse withdrawn windows. Not removing the
    property upon shutdown allows the next Window Manager to restore
    windows to their previous state.

    An implementation MAY add new atoms to this list. Implementations
    without extensions MUST ignore any unknown atoms, effectively removing
    them from the list. These extension atoms MUST NOT start with the
    prefix _NET.

    _NET_WM_STATE_MODAL indicates that this is a modal dialog box. If the
    WM_TRANSIENT_FOR hint is set to another toplevel window, the dialog is
    modal for that window; if WM_TRANSIENT_FOR is not set or set to the
    root window the dialog is modal for its window group.

    _NET_WM_STATE_STICKY indicates that the Window Manager SHOULD keep the
    window's position fixed on the screen, even when the virtual desktop
    scrolls.

    _NET_WM_STATE_MAXIMIZED_{VERT,HORZ} indicates that the window is
    {vertically,horizontally} maximized.

    _NET_WM_STATE_SHADED indicates that the window is shaded.

    _NET_WM_STATE_SKIP_TASKBAR indicates that the window should not be
    included on a taskbar. This hint should be requested by the
    application, i.e. it indicates that the window by nature is never in
    the taskbar. Applications should not set this hint if
    _NET_WM_WINDOW_TYPE already conveys the exact nature of the window.

    _NET_WM_STATE_SKIP_PAGER indicates that the window should not be
    included on a Pager. This hint should be requested by the application,
    i.e. it indicates that the window by nature is never in the Pager.
    Applications should not set this hint if _NET_WM_WINDOW_TYPE already
    conveys the exact nature of the window.

    _NET_WM_STATE_HIDDEN should be set by the Window Manager to indicate
    that a window would not be visible on the screen if its
    desktop/viewport were active and its coordinates were within the screen
    bounds. The canonical example is that minimized windows should be in
    the _NET_WM_STATE_HIDDEN state. Pagers and similar applications should
    use _NET_WM_STATE_HIDDEN instead of WM_STATE to decide whether to
    display a window in miniature representations of the windows on a
    desktop.

    Implementation note: if an Application asks to toggle
    _NET_WM_STATE_HIDDEN the Window Manager should probably just ignore the
    request, since _NET_WM_STATE_HIDDEN is a function of some other aspect
    of the window such as minimization, rather than an independent state.

    _NET_WM_STATE_FULLSCREEN indicates that the window should fill the
    entire screen and have no window decorations. Additionally the Window
    Manager is responsible for restoring the original geometry after a
    switch from fullscreen back to normal window. For example, a
    presentation program would use this hint.

    _NET_WM_STATE_ABOVE indicates that the window should be on top of most
    windows (see the section called "Stacking order" for details).

    _NET_WM_STATE_BELOW indicates that the window should be below most
    windows (see the section called "Stacking order" for details).

    _NET_WM_STATE_ABOVE and _NET_WM_STATE_BELOW are mainly meant for user
    preferences and should not be used by applications e.g. for drawing
    attention to their dialogs (the Urgency hint should be used in that
    case, see the section called "Urgency").'

    _NET_WM_STATE_DEMANDS_ATTENTION indicates that some action in or with
    the window happened. For example, it may be set by the Window Manager
    if the window requested activation but the Window Manager refused it,
    or the application may set it if it finished some work. This state may
    be set by both the Client and the Window Manager. It should be unset by
    the Window Manager when it decides the window got the required
    attention (usually, that it got activated).

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @return:        A list of atoms corresponding to this window's state.
    @rtype:         util.PropertyCookie (ATOM[]/32)
    """
    return util.PropertyCookie(
        util.get_property(c, window, atom(c, '_NET_WM_STATE')))

def get_wm_state_unchecked(c, window):
    """
    Get a list of atoms representing the state of the window.

    A list of hints describing the window state. Atoms present in the list
    MUST be considered set, atoms not present in the list MUST be
    considered not set. The Window Manager SHOULD honor _NET_WM_STATE
    whenever a withdrawn window requests to be mapped. A Client wishing to
    change the state of a window MUST send a _NET_WM_STATE client message
    to the root window (see below). The Window Manager MUST keep this
    property updated to reflect the current state of the window.

    The Window Manager should remove the property whenever a window is
    withdrawn, but it should leave the property in place when it is
    shutting down, e.g. in response to losing ownership of the WM_Sn
    manager selection.

    Rationale: Removing the property upon window withdrawal helps legacy
    applications which want to reuse withdrawn windows. Not removing the
    property upon shutdown allows the next Window Manager to restore
    windows to their previous state.

    An implementation MAY add new atoms to this list. Implementations
    without extensions MUST ignore any unknown atoms, effectively removing
    them from the list. These extension atoms MUST NOT start with the
    prefix _NET.

    _NET_WM_STATE_MODAL indicates that this is a modal dialog box. If the
    WM_TRANSIENT_FOR hint is set to another toplevel window, the dialog is
    modal for that window; if WM_TRANSIENT_FOR is not set or set to the
    root window the dialog is modal for its window group.

    _NET_WM_STATE_STICKY indicates that the Window Manager SHOULD keep the
    window's position fixed on the screen, even when the virtual desktop
    scrolls.

    _NET_WM_STATE_MAXIMIZED_{VERT,HORZ} indicates that the window is
    {vertically,horizontally} maximized.

    _NET_WM_STATE_SHADED indicates that the window is shaded.

    _NET_WM_STATE_SKIP_TASKBAR indicates that the window should not be
    included on a taskbar. This hint should be requested by the
    application, i.e. it indicates that the window by nature is never in
    the taskbar. Applications should not set this hint if
    _NET_WM_WINDOW_TYPE already conveys the exact nature of the window.

    _NET_WM_STATE_SKIP_PAGER indicates that the window should not be
    included on a Pager. This hint should be requested by the application,
    i.e. it indicates that the window by nature is never in the Pager.
    Applications should not set this hint if _NET_WM_WINDOW_TYPE already
    conveys the exact nature of the window.

    _NET_WM_STATE_HIDDEN should be set by the Window Manager to indicate
    that a window would not be visible on the screen if its
    desktop/viewport were active and its coordinates were within the screen
    bounds. The canonical example is that minimized windows should be in
    the _NET_WM_STATE_HIDDEN state. Pagers and similar applications should
    use _NET_WM_STATE_HIDDEN instead of WM_STATE to decide whether to
    display a window in miniature representations of the windows on a
    desktop.

    Implementation note: if an Application asks to toggle
    _NET_WM_STATE_HIDDEN the Window Manager should probably just ignore the
    request, since _NET_WM_STATE_HIDDEN is a function of some other aspect
    of the window such as minimization, rather than an independent state.

    _NET_WM_STATE_FULLSCREEN indicates that the window should fill the
    entire screen and have no window decorations. Additionally the Window
    Manager is responsible for restoring the original geometry after a
    switch from fullscreen back to normal window. For example, a
    presentation program would use this hint.

    _NET_WM_STATE_ABOVE indicates that the window should be on top of most
    windows (see the section called "Stacking order" for details).

    _NET_WM_STATE_BELOW indicates that the window should be below most
    windows (see the section called "Stacking order" for details).

    _NET_WM_STATE_ABOVE and _NET_WM_STATE_BELOW are mainly meant for user
    preferences and should not be used by applications e.g. for drawing
    attention to their dialogs (the Urgency hint should be used in that
    case, see the section called "Urgency").'

    _NET_WM_STATE_DEMANDS_ATTENTION indicates that some action in or with
    the window happened. For example, it may be set by the Window Manager
    if the window requested activation but the Window Manager refused it,
    or the application may set it if it finished some work. This state may
    be set by both the Client and the Window Manager. It should be unset by
    the Window Manager when it decides the window got the required
    attention (usually, that it got activated).

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @return:        A list of atoms corresponding to this window's state.
    @rtype:         util.PropertyCookie (ATOM[]/32)
    """
    return util.PropertyCookie(
        util.get_property_unchecked(c, window, atom(c, '_NET_WM_STATE')))

def set_wm_state(c, window, states):
    """
    Sets the list of atoms representing this window's state.

    A list of hints describing the window state. Atoms present in the list
    MUST be considered set, atoms not present in the list MUST be
    considered not set. The Window Manager SHOULD honor _NET_WM_STATE
    whenever a withdrawn window requests to be mapped. A Client wishing to
    change the state of a window MUST send a _NET_WM_STATE client message
    to the root window (see below). The Window Manager MUST keep this
    property updated to reflect the current state of the window.

    The Window Manager should remove the property whenever a window is
    withdrawn, but it should leave the property in place when it is
    shutting down, e.g. in response to losing ownership of the WM_Sn
    manager selection.

    Rationale: Removing the property upon window withdrawal helps legacy
    applications which want to reuse withdrawn windows. Not removing the
    property upon shutdown allows the next Window Manager to restore
    windows to their previous state.

    An implementation MAY add new atoms to this list. Implementations
    without extensions MUST ignore any unknown atoms, effectively removing
    them from the list. These extension atoms MUST NOT start with the
    prefix _NET.

    _NET_WM_STATE_MODAL indicates that this is a modal dialog box. If the
    WM_TRANSIENT_FOR hint is set to another toplevel window, the dialog is
    modal for that window; if WM_TRANSIENT_FOR is not set or set to the
    root window the dialog is modal for its window group.

    _NET_WM_STATE_STICKY indicates that the Window Manager SHOULD keep the
    window's position fixed on the screen, even when the virtual desktop
    scrolls.

    _NET_WM_STATE_MAXIMIZED_{VERT,HORZ} indicates that the window is
    {vertically,horizontally} maximized.

    _NET_WM_STATE_SHADED indicates that the window is shaded.

    _NET_WM_STATE_SKIP_TASKBAR indicates that the window should not be
    included on a taskbar. This hint should be requested by the
    application, i.e. it indicates that the window by nature is never in
    the taskbar. Applications should not set this hint if
    _NET_WM_WINDOW_TYPE already conveys the exact nature of the window.

    _NET_WM_STATE_SKIP_PAGER indicates that the window should not be
    included on a Pager. This hint should be requested by the application,
    i.e. it indicates that the window by nature is never in the Pager.
    Applications should not set this hint if _NET_WM_WINDOW_TYPE already
    conveys the exact nature of the window.

    _NET_WM_STATE_HIDDEN should be set by the Window Manager to indicate
    that a window would not be visible on the screen if its
    desktop/viewport were active and its coordinates were within the screen
    bounds. The canonical example is that minimized windows should be in
    the _NET_WM_STATE_HIDDEN state. Pagers and similar applications should
    use _NET_WM_STATE_HIDDEN instead of WM_STATE to decide whether to
    display a window in miniature representations of the windows on a
    desktop.

    Implementation note: if an Application asks to toggle
    _NET_WM_STATE_HIDDEN the Window Manager should probably just ignore the
    request, since _NET_WM_STATE_HIDDEN is a function of some other aspect
    of the window such as minimization, rather than an independent state.

    _NET_WM_STATE_FULLSCREEN indicates that the window should fill the
    entire screen and have no window decorations. Additionally the Window
    Manager is responsible for restoring the original geometry after a
    switch from fullscreen back to normal window. For example, a
    presentation program would use this hint.

    _NET_WM_STATE_ABOVE indicates that the window should be on top of most
    windows (see the section called "Stacking order" for details).

    _NET_WM_STATE_BELOW indicates that the window should be below most
    windows (see the section called "Stacking order" for details).

    _NET_WM_STATE_ABOVE and _NET_WM_STATE_BELOW are mainly meant for user
    preferences and should not be used by applications e.g. for drawing
    attention to their dialogs (the Urgency hint should be used in that
    case, see the section called "Urgency").'

    _NET_WM_STATE_DEMANDS_ATTENTION indicates that some action in or with
    the window happened. For example, it may be set by the Window Manager
    if the window requested activation but the Window Manager refused it,
    or the application may set it if it finished some work. This state may
    be set by both the Client and the Window Manager. It should be unset by
    the Window Manager when it decides the window got the required
    attention (usually, that it got activated).

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @param states:  A list of window state atoms.
    @type states:   ATOM[]/32
    @rtype:         xcb.VoidCookie
    """
    packed = struct.pack('I' * len(states), *states)
    return c.core.ChangeProperty(xcb.xproto.PropMode.Replace, window,
                                 atom(c, '_NET_WM_STATE'),
                                 xcb.xproto.Atom.ATOM, 32, len(states),
                                 packed)

def set_wm_state_checked(c, window, states):
    """
    Sets the list of atoms representing this window's state.

    A list of hints describing the window state. Atoms present in the list
    MUST be considered set, atoms not present in the list MUST be
    considered not set. The Window Manager SHOULD honor _NET_WM_STATE
    whenever a withdrawn window requests to be mapped. A Client wishing to
    change the state of a window MUST send a _NET_WM_STATE client message
    to the root window (see below). The Window Manager MUST keep this
    property updated to reflect the current state of the window.

    The Window Manager should remove the property whenever a window is
    withdrawn, but it should leave the property in place when it is
    shutting down, e.g. in response to losing ownership of the WM_Sn
    manager selection.

    Rationale: Removing the property upon window withdrawal helps legacy
    applications which want to reuse withdrawn windows. Not removing the
    property upon shutdown allows the next Window Manager to restore
    windows to their previous state.

    An implementation MAY add new atoms to this list. Implementations
    without extensions MUST ignore any unknown atoms, effectively removing
    them from the list. These extension atoms MUST NOT start with the
    prefix _NET.

    _NET_WM_STATE_MODAL indicates that this is a modal dialog box. If the
    WM_TRANSIENT_FOR hint is set to another toplevel window, the dialog is
    modal for that window; if WM_TRANSIENT_FOR is not set or set to the
    root window the dialog is modal for its window group.

    _NET_WM_STATE_STICKY indicates that the Window Manager SHOULD keep the
    window's position fixed on the screen, even when the virtual desktop
    scrolls.

    _NET_WM_STATE_MAXIMIZED_{VERT,HORZ} indicates that the window is
    {vertically,horizontally} maximized.

    _NET_WM_STATE_SHADED indicates that the window is shaded.

    _NET_WM_STATE_SKIP_TASKBAR indicates that the window should not be
    included on a taskbar. This hint should be requested by the
    application, i.e. it indicates that the window by nature is never in
    the taskbar. Applications should not set this hint if
    _NET_WM_WINDOW_TYPE already conveys the exact nature of the window.

    _NET_WM_STATE_SKIP_PAGER indicates that the window should not be
    included on a Pager. This hint should be requested by the application,
    i.e. it indicates that the window by nature is never in the Pager.
    Applications should not set this hint if _NET_WM_WINDOW_TYPE already
    conveys the exact nature of the window.

    _NET_WM_STATE_HIDDEN should be set by the Window Manager to indicate
    that a window would not be visible on the screen if its
    desktop/viewport were active and its coordinates were within the screen
    bounds. The canonical example is that minimized windows should be in
    the _NET_WM_STATE_HIDDEN state. Pagers and similar applications should
    use _NET_WM_STATE_HIDDEN instead of WM_STATE to decide whether to
    display a window in miniature representations of the windows on a
    desktop.

    Implementation note: if an Application asks to toggle
    _NET_WM_STATE_HIDDEN the Window Manager should probably just ignore the
    request, since _NET_WM_STATE_HIDDEN is a function of some other aspect
    of the window such as minimization, rather than an independent state.

    _NET_WM_STATE_FULLSCREEN indicates that the window should fill the
    entire screen and have no window decorations. Additionally the Window
    Manager is responsible for restoring the original geometry after a
    switch from fullscreen back to normal window. For example, a
    presentation program would use this hint.

    _NET_WM_STATE_ABOVE indicates that the window should be on top of most
    windows (see the section called "Stacking order" for details).

    _NET_WM_STATE_BELOW indicates that the window should be below most
    windows (see the section called "Stacking order" for details).

    _NET_WM_STATE_ABOVE and _NET_WM_STATE_BELOW are mainly meant for user
    preferences and should not be used by applications e.g. for drawing
    attention to their dialogs (the Urgency hint should be used in that
    case, see the section called "Urgency").'

    _NET_WM_STATE_DEMANDS_ATTENTION indicates that some action in or with
    the window happened. For example, it may be set by the Window Manager
    if the window requested activation but the Window Manager refused it,
    or the application may set it if it finished some work. This state may
    be set by both the Client and the Window Manager. It should be unset by
    the Window Manager when it decides the window got the required
    attention (usually, that it got activated).

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @param states:  A list of window state atoms.
    @type states:   ATOM[]/32
    @rtype:         xcb.VoidCookie
    """
    packed = struct.pack('I' * len(states), *states)
    return c.core.ChangePropertyChecked(xcb.xproto.PropMode.Replace, window,
                                        atom(c, '_NET_WM_STATE'),
                                        xcb.xproto.Atom.ATOM, 32, len(states),
                                        packed)

def request_wm_state(c, window, action, first, second=0, source=1):
    """
    Sends an event to root window to change the state of the window.

    A list of hints describing the window state. Atoms present in the list
    MUST be considered set, atoms not present in the list MUST be
    considered not set. The Window Manager SHOULD honor _NET_WM_STATE
    whenever a withdrawn window requests to be mapped. A Client wishing to
    change the state of a window MUST send a _NET_WM_STATE client message
    to the root window (see below). The Window Manager MUST keep this
    property updated to reflect the current state of the window.

    The Window Manager should remove the property whenever a window is
    withdrawn, but it should leave the property in place when it is
    shutting down, e.g. in response to losing ownership of the WM_Sn
    manager selection.

    Rationale: Removing the property upon window withdrawal helps legacy
    applications which want to reuse withdrawn windows. Not removing the
    property upon shutdown allows the next Window Manager to restore
    windows to their previous state.

    An implementation MAY add new atoms to this list. Implementations
    without extensions MUST ignore any unknown atoms, effectively removing
    them from the list. These extension atoms MUST NOT start with the
    prefix _NET.

    _NET_WM_STATE_MODAL indicates that this is a modal dialog box. If the
    WM_TRANSIENT_FOR hint is set to another toplevel window, the dialog is
    modal for that window; if WM_TRANSIENT_FOR is not set or set to the
    root window the dialog is modal for its window group.

    _NET_WM_STATE_STICKY indicates that the Window Manager SHOULD keep the
    window's position fixed on the screen, even when the virtual desktop
    scrolls.

    _NET_WM_STATE_MAXIMIZED_{VERT,HORZ} indicates that the window is
    {vertically,horizontally} maximized.

    _NET_WM_STATE_SHADED indicates that the window is shaded.

    _NET_WM_STATE_SKIP_TASKBAR indicates that the window should not be
    included on a taskbar. This hint should be requested by the
    application, i.e. it indicates that the window by nature is never in
    the taskbar. Applications should not set this hint if
    _NET_WM_WINDOW_TYPE already conveys the exact nature of the window.

    _NET_WM_STATE_SKIP_PAGER indicates that the window should not be
    included on a Pager. This hint should be requested by the application,
    i.e. it indicates that the window by nature is never in the Pager.
    Applications should not set this hint if _NET_WM_WINDOW_TYPE already
    conveys the exact nature of the window.

    _NET_WM_STATE_HIDDEN should be set by the Window Manager to indicate
    that a window would not be visible on the screen if its
    desktop/viewport were active and its coordinates were within the screen
    bounds. The canonical example is that minimized windows should be in
    the _NET_WM_STATE_HIDDEN state. Pagers and similar applications should
    use _NET_WM_STATE_HIDDEN instead of WM_STATE to decide whether to
    display a window in miniature representations of the windows on a
    desktop.

    Implementation note: if an Application asks to toggle
    _NET_WM_STATE_HIDDEN the Window Manager should probably just ignore the
    request, since _NET_WM_STATE_HIDDEN is a function of some other aspect
    of the window such as minimization, rather than an independent state.

    _NET_WM_STATE_FULLSCREEN indicates that the window should fill the
    entire screen and have no window decorations. Additionally the Window
    Manager is responsible for restoring the original geometry after a
    switch from fullscreen back to normal window. For example, a
    presentation program would use this hint.

    _NET_WM_STATE_ABOVE indicates that the window should be on top of most
    windows (see the section called "Stacking order" for details).

    _NET_WM_STATE_BELOW indicates that the window should be below most
    windows (see the section called "Stacking order" for details).

    _NET_WM_STATE_ABOVE and _NET_WM_STATE_BELOW are mainly meant for user
    preferences and should not be used by applications e.g. for drawing
    attention to their dialogs (the Urgency hint should be used in that
    case, see the section called "Urgency").'

    _NET_WM_STATE_DEMANDS_ATTENTION indicates that some action in or with
    the window happened. For example, it may be set by the Window Manager
    if the window requested activation but the Window Manager refused it,
    or the application may set it if it finished some work. This state may
    be set by both the Client and the Window Manager. It should be unset by
    the Window Manager when it decides the window got the required
    attention (usually, that it got activated).

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @param action:  The kind of state action to perform. I tshould be one
                    of the following flags:

                    _NET_WM_STATE_REMOVE    = 0
                    _NET_WM_STATE_ADD       = 1
                    _NET_WM_STATE_TOGGLE    = 2
    @param first:   The first property to be changed.
    @param second:  The second property to be changed (should be 0 if only
                    one property is being changed).
    @param source:  The source indication.
    @rtype:         xcb.VoidCookie
    """
    return revent(c, window, atom(c, '_NET_WM_STATE'), [action, first,
                  second, source])

def request_wm_state_checked(c, window, action, first, second=0, source=1):
    """
    Sends an event to root window to change the state of the window.

    A list of hints describing the window state. Atoms present in the list
    MUST be considered set, atoms not present in the list MUST be
    considered not set. The Window Manager SHOULD honor _NET_WM_STATE
    whenever a withdrawn window requests to be mapped. A Client wishing to
    change the state of a window MUST send a _NET_WM_STATE client message
    to the root window (see below). The Window Manager MUST keep this
    property updated to reflect the current state of the window.

    The Window Manager should remove the property whenever a window is
    withdrawn, but it should leave the property in place when it is
    shutting down, e.g. in response to losing ownership of the WM_Sn
    manager selection.

    Rationale: Removing the property upon window withdrawal helps legacy
    applications which want to reuse withdrawn windows. Not removing the
    property upon shutdown allows the next Window Manager to restore
    windows to their previous state.

    An implementation MAY add new atoms to this list. Implementations
    without extensions MUST ignore any unknown atoms, effectively removing
    them from the list. These extension atoms MUST NOT start with the
    prefix _NET.

    _NET_WM_STATE_MODAL indicates that this is a modal dialog box. If the
    WM_TRANSIENT_FOR hint is set to another toplevel window, the dialog is
    modal for that window; if WM_TRANSIENT_FOR is not set or set to the
    root window the dialog is modal for its window group.

    _NET_WM_STATE_STICKY indicates that the Window Manager SHOULD keep the
    window's position fixed on the screen, even when the virtual desktop
    scrolls.

    _NET_WM_STATE_MAXIMIZED_{VERT,HORZ} indicates that the window is
    {vertically,horizontally} maximized.

    _NET_WM_STATE_SHADED indicates that the window is shaded.

    _NET_WM_STATE_SKIP_TASKBAR indicates that the window should not be
    included on a taskbar. This hint should be requested by the
    application, i.e. it indicates that the window by nature is never in
    the taskbar. Applications should not set this hint if
    _NET_WM_WINDOW_TYPE already conveys the exact nature of the window.

    _NET_WM_STATE_SKIP_PAGER indicates that the window should not be
    included on a Pager. This hint should be requested by the application,
    i.e. it indicates that the window by nature is never in the Pager.
    Applications should not set this hint if _NET_WM_WINDOW_TYPE already
    conveys the exact nature of the window.

    _NET_WM_STATE_HIDDEN should be set by the Window Manager to indicate
    that a window would not be visible on the screen if its
    desktop/viewport were active and its coordinates were within the screen
    bounds. The canonical example is that minimized windows should be in
    the _NET_WM_STATE_HIDDEN state. Pagers and similar applications should
    use _NET_WM_STATE_HIDDEN instead of WM_STATE to decide whether to
    display a window in miniature representations of the windows on a
    desktop.

    Implementation note: if an Application asks to toggle
    _NET_WM_STATE_HIDDEN the Window Manager should probably just ignore the
    request, since _NET_WM_STATE_HIDDEN is a function of some other aspect
    of the window such as minimization, rather than an independent state.

    _NET_WM_STATE_FULLSCREEN indicates that the window should fill the
    entire screen and have no window decorations. Additionally the Window
    Manager is responsible for restoring the original geometry after a
    switch from fullscreen back to normal window. For example, a
    presentation program would use this hint.

    _NET_WM_STATE_ABOVE indicates that the window should be on top of most
    windows (see the section called "Stacking order" for details).

    _NET_WM_STATE_BELOW indicates that the window should be below most
    windows (see the section called "Stacking order" for details).

    _NET_WM_STATE_ABOVE and _NET_WM_STATE_BELOW are mainly meant for user
    preferences and should not be used by applications e.g. for drawing
    attention to their dialogs (the Urgency hint should be used in that
    case, see the section called "Urgency").'

    _NET_WM_STATE_DEMANDS_ATTENTION indicates that some action in or with
    the window happened. For example, it may be set by the Window Manager
    if the window requested activation but the Window Manager refused it,
    or the application may set it if it finished some work. This state may
    be set by both the Client and the Window Manager. It should be unset by
    the Window Manager when it decides the window got the required
    attention (usually, that it got activated).

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @param action:  The kind of state action to perform. I tshould be one
                    of the following flags:

                    _NET_WM_STATE_REMOVE    = 0
                    _NET_WM_STATE_ADD       = 1
                    _NET_WM_STATE_TOGGLE    = 2
    @param first:   The first property to be changed.
    @param second:  The second property to be changed (should be 0 if only
                    one property is being changed).
    @param source:  The source indication.
    @rtype:         xcb.VoidCookie
    """
    return revent_checked(c, window, atom(c, '_NET_WM_STATE'), [action, first,
                  second, source])

# _NET_WM_ALLOWED_ACTIONS

def get_wm_allowed_actions(c, window):
    """
    Get a list of atoms representing the WM supported actions on a window.

    A list of atoms indicating user operations that the Window Manager
    supports for this window. Atoms present in the list indicate allowed
    actions, atoms not present in the list indicate actions that are not
    supported for this window. The Window Manager MUST keep this property
    updated to reflect the actions which are currently "active" or
    "sensitive" for a window. Taskbars, Pagers, and other tools use
    _NET_WM_ALLOWED_ACTIONS to decide which actions should be made
    available to the user.

    An implementation MAY add new atoms to this list. Implementations
    without extensions MUST ignore any unknown atoms, effectively removing
    them from the list. These extension atoms MUST NOT start with the
    prefix _NET.

    Note that the actions listed here are those that the Window Manager
    will honor for this window. The operations must still be requested
    through the normal mechanisms outlined in this specification. For
    example, _NET_WM_ACTION_CLOSE does not mean that clients can send a
    WM_DELETE_WINDOW message to this window; it means that clients can use
    a _NET_CLOSE_WINDOW message to ask the Window Manager to do so.

    Window Managers SHOULD ignore the value of _NET_WM_ALLOWED_ACTIONS when
    they initially manage a window. This value may be left over from a
    previous Window Manager with different policies.

    _NET_WM_ACTION_MOVE indicates that the window may be moved around the
    screen.

    _NET_WM_ACTION_RESIZE indicates that the window may be resized.
    (Implementation note: Window Managers can identify a non-resizable
    window because its minimum and maximum size in WM_NORMAL_HINTS will be
    the same.)

    _NET_WM_ACTION_MINIMIZE indicates that the window may be iconified.

    _NET_WM_ACTION_SHADE indicates that the window may be shaded.

    _NET_WM_ACTION_STICK indicates that the window may have its sticky
    state toggled (as for _NET_WM_STATE_STICKY). Note that this state has
    to do with viewports, not desktops.

    _NET_WM_ACTION_MAXIMIZE_HORZ indicates that the window may be maximized
    horizontally.

    _NET_WM_ACTION_MAXIMIZE_VERT indicates that the window may be maximized
    vertically.

    _NET_WM_ACTION_FULLSCREEN indicates that the window may be brought to
    fullscreen state.

    _NET_WM_ACTION_CHANGE_DESKTOP indicates that the window may be moved
    between desktops.

    _NET_WM_ACTION_CLOSE indicates that the window may be closed (i.e. a
    _NET_CLOSE_WINDOW message may be sent).

    _NET_WM_ACTION_ABOVE indicates that the window may placed in the
    "above" layer of windows (i.e. will respond to _NET_WM_STATE_ABOVE
    changes; see also the section called "Stacking order" for details).

    _NET_WM_ACTION_BELOW indicates that the window may placed in the
    "below" layer of windows (i.e. will respond to _NET_WM_STATE_BELOW
    changes; see also the section called "Stacking order" for details)).

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @return:        A list of atoms corresponding to this window's supported
                    actions through the window manager.
    @rtype:         util.PropertyCookie (ATOM[]/32)
    """
    return util.PropertyCookie(
        util.get_property(c, window, atom(c, '_NET_WM_ALLOWED_ACTIONS')))

def get_wm_allowed_actions_unchecked(c, window):
    """
    Get a list of atoms representing the WM supported actions on a window.

    A list of atoms indicating user operations that the Window Manager
    supports for this window. Atoms present in the list indicate allowed
    actions, atoms not present in the list indicate actions that are not
    supported for this window. The Window Manager MUST keep this property
    updated to reflect the actions which are currently "active" or
    "sensitive" for a window. Taskbars, Pagers, and other tools use
    _NET_WM_ALLOWED_ACTIONS to decide which actions should be made
    available to the user.

    An implementation MAY add new atoms to this list. Implementations
    without extensions MUST ignore any unknown atoms, effectively removing
    them from the list. These extension atoms MUST NOT start with the
    prefix _NET.

    Note that the actions listed here are those that the Window Manager
    will honor for this window. The operations must still be requested
    through the normal mechanisms outlined in this specification. For
    example, _NET_WM_ACTION_CLOSE does not mean that clients can send a
    WM_DELETE_WINDOW message to this window; it means that clients can use
    a _NET_CLOSE_WINDOW message to ask the Window Manager to do so.

    Window Managers SHOULD ignore the value of _NET_WM_ALLOWED_ACTIONS when
    they initially manage a window. This value may be left over from a
    previous Window Manager with different policies.

    _NET_WM_ACTION_MOVE indicates that the window may be moved around the
    screen.

    _NET_WM_ACTION_RESIZE indicates that the window may be resized.
    (Implementation note: Window Managers can identify a non-resizable
    window because its minimum and maximum size in WM_NORMAL_HINTS will be
    the same.)

    _NET_WM_ACTION_MINIMIZE indicates that the window may be iconified.

    _NET_WM_ACTION_SHADE indicates that the window may be shaded.

    _NET_WM_ACTION_STICK indicates that the window may have its sticky
    state toggled (as for _NET_WM_STATE_STICKY). Note that this state has
    to do with viewports, not desktops.

    _NET_WM_ACTION_MAXIMIZE_HORZ indicates that the window may be maximized
    horizontally.

    _NET_WM_ACTION_MAXIMIZE_VERT indicates that the window may be maximized
    vertically.

    _NET_WM_ACTION_FULLSCREEN indicates that the window may be brought to
    fullscreen state.

    _NET_WM_ACTION_CHANGE_DESKTOP indicates that the window may be moved
    between desktops.

    _NET_WM_ACTION_CLOSE indicates that the window may be closed (i.e. a
    _NET_CLOSE_WINDOW message may be sent).

    _NET_WM_ACTION_ABOVE indicates that the window may placed in the
    "above" layer of windows (i.e. will respond to _NET_WM_STATE_ABOVE
    changes; see also the section called "Stacking order" for details).

    _NET_WM_ACTION_BELOW indicates that the window may placed in the
    "below" layer of windows (i.e. will respond to _NET_WM_STATE_BELOW
    changes; see also the section called "Stacking order" for details)).

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @return:        A list of atoms corresponding to this window's supported
                    actions through the window manager.
    @rtype:         util.PropertyCookie (ATOM[]/32)
    """
    return util.PropertyCookie(
        util.get_property_unchecked(c, window,
                                    atom(c, '_NET_WM_ALLOWED_ACTIONS')))

def set_wm_allowed_actions(c, window, actions):
    """
    Sets the list of atoms representing the WM supported actions on a window.

    A list of atoms indicating user operations that the Window Manager
    supports for this window. Atoms present in the list indicate allowed
    actions, atoms not present in the list indicate actions that are not
    supported for this window. The Window Manager MUST keep this property
    updated to reflect the actions which are currently "active" or
    "sensitive" for a window. Taskbars, Pagers, and other tools use
    _NET_WM_ALLOWED_ACTIONS to decide which actions should be made
    available to the user.

    An implementation MAY add new atoms to this list. Implementations
    without extensions MUST ignore any unknown atoms, effectively removing
    them from the list. These extension atoms MUST NOT start with the
    prefix _NET.

    Note that the actions listed here are those that the Window Manager
    will honor for this window. The operations must still be requested
    through the normal mechanisms outlined in this specification. For
    example, _NET_WM_ACTION_CLOSE does not mean that clients can send a
    WM_DELETE_WINDOW message to this window; it means that clients can use
    a _NET_CLOSE_WINDOW message to ask the Window Manager to do so.

    Window Managers SHOULD ignore the value of _NET_WM_ALLOWED_ACTIONS when
    they initially manage a window. This value may be left over from a
    previous Window Manager with different policies.

    _NET_WM_ACTION_MOVE indicates that the window may be moved around the
    screen.

    _NET_WM_ACTION_RESIZE indicates that the window may be resized.
    (Implementation note: Window Managers can identify a non-resizable
    window because its minimum and maximum size in WM_NORMAL_HINTS will be
    the same.)

    _NET_WM_ACTION_MINIMIZE indicates that the window may be iconified.

    _NET_WM_ACTION_SHADE indicates that the window may be shaded.

    _NET_WM_ACTION_STICK indicates that the window may have its sticky
    state toggled (as for _NET_WM_STATE_STICKY). Note that this state has
    to do with viewports, not desktops.

    _NET_WM_ACTION_MAXIMIZE_HORZ indicates that the window may be maximized
    horizontally.

    _NET_WM_ACTION_MAXIMIZE_VERT indicates that the window may be maximized
    vertically.

    _NET_WM_ACTION_FULLSCREEN indicates that the window may be brought to
    fullscreen state.

    _NET_WM_ACTION_CHANGE_DESKTOP indicates that the window may be moved
    between desktops.

    _NET_WM_ACTION_CLOSE indicates that the window may be closed (i.e. a
    _NET_CLOSE_WINDOW message may be sent).

    _NET_WM_ACTION_ABOVE indicates that the window may placed in the
    "above" layer of windows (i.e. will respond to _NET_WM_STATE_ABOVE
    changes; see also the section called "Stacking order" for details).

    _NET_WM_ACTION_BELOW indicates that the window may placed in the
    "below" layer of windows (i.e. will respond to _NET_WM_STATE_BELOW
    changes; see also the section called "Stacking order" for details)).

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @param actions:  A list of allowable action atoms.
    @type actions:   ATOM[]/32
    @rtype:         xcb.VoidCookie
    """
    packed = struct.pack('I' * len(actions), *actions)
    return c.core.ChangeProperty(xcb.xproto.PropMode.Replace, window,
                                 atom(c, '_NET_WM_ALLOWED_ACTIONS'),
                                 xcb.xproto.Atom.ATOM, 32, len(actions),
                                 packed)

def set_wm_allowed_actions_checked(c, window, actions):
    """
    Sets the list of atoms representing the WM supported actions on a window.

    A list of atoms indicating user operations that the Window Manager
    supports for this window. Atoms present in the list indicate allowed
    actions, atoms not present in the list indicate actions that are not
    supported for this window. The Window Manager MUST keep this property
    updated to reflect the actions which are currently "active" or
    "sensitive" for a window. Taskbars, Pagers, and other tools use
    _NET_WM_ALLOWED_ACTIONS to decide which actions should be made
    available to the user.

    An implementation MAY add new atoms to this list. Implementations
    without extensions MUST ignore any unknown atoms, effectively removing
    them from the list. These extension atoms MUST NOT start with the
    prefix _NET.

    Note that the actions listed here are those that the Window Manager
    will honor for this window. The operations must still be requested
    through the normal mechanisms outlined in this specification. For
    example, _NET_WM_ACTION_CLOSE does not mean that clients can send a
    WM_DELETE_WINDOW message to this window; it means that clients can use
    a _NET_CLOSE_WINDOW message to ask the Window Manager to do so.

    Window Managers SHOULD ignore the value of _NET_WM_ALLOWED_ACTIONS when
    they initially manage a window. This value may be left over from a
    previous Window Manager with different policies.

    _NET_WM_ACTION_MOVE indicates that the window may be moved around the
    screen.

    _NET_WM_ACTION_RESIZE indicates that the window may be resized.
    (Implementation note: Window Managers can identify a non-resizable
    window because its minimum and maximum size in WM_NORMAL_HINTS will be
    the same.)

    _NET_WM_ACTION_MINIMIZE indicates that the window may be iconified.

    _NET_WM_ACTION_SHADE indicates that the window may be shaded.

    _NET_WM_ACTION_STICK indicates that the window may have its sticky
    state toggled (as for _NET_WM_STATE_STICKY). Note that this state has
    to do with viewports, not desktops.

    _NET_WM_ACTION_MAXIMIZE_HORZ indicates that the window may be maximized
    horizontally.

    _NET_WM_ACTION_MAXIMIZE_VERT indicates that the window may be maximized
    vertically.

    _NET_WM_ACTION_FULLSCREEN indicates that the window may be brought to
    fullscreen state.

    _NET_WM_ACTION_CHANGE_DESKTOP indicates that the window may be moved
    between desktops.

    _NET_WM_ACTION_CLOSE indicates that the window may be closed (i.e. a
    _NET_CLOSE_WINDOW message may be sent).

    _NET_WM_ACTION_ABOVE indicates that the window may placed in the
    "above" layer of windows (i.e. will respond to _NET_WM_STATE_ABOVE
    changes; see also the section called "Stacking order" for details).

    _NET_WM_ACTION_BELOW indicates that the window may placed in the
    "below" layer of windows (i.e. will respond to _NET_WM_STATE_BELOW
    changes; see also the section called "Stacking order" for details)).

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @param actions:  A list of allowable action atoms.
    @type actions:   ATOM[]/32
    @rtype:         xcb.VoidCookie
    """
    packed = struct.pack('I' * len(actions), *actions)
    return c.core.ChangePropertyChecked(xcb.xproto.PropMode.Replace, window,
                                        atom(c, '_NET_WM_ALLOWED_ACTIONS'),
                                        xcb.xproto.Atom.ATOM, 32, len(actions),
                                        packed)

# _NET_WM_STRUT

class StrutCookie(util.PropertyCookie):
    def reply(self):
        v = util.PropertyCookie.reply(self)

        if not v:
            return None

        return {
            'left': v[0],
            'right': v[1],
            'top': v[2],
            'bottom': v[3]
        }

def get_wm_strut(c, window):
    """
    Returns the struts for a window.

    This property is equivalent to a _NET_WM_STRUT_PARTIAL property where
    all start values are 0 and all end values are the height or width of
    the logical screen. _NET_WM_STRUT_PARTIAL was introduced later than
    _NET_WM_STRUT, however, so clients MAY set this property in addition to
    _NET_WM_STRUT_PARTIAL to ensure backward compatibility with Window
    Managers supporting older versions of the Specification.

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @return:        A strut dictionary.

                    Keys: left, right, top, bottom
    @rtype:         StrutCookie (CARDINAL[4]/32)
    """
    return StrutCookie(
        util.get_property(c, window, atom(c, '_NET_WM_STRUT')))

def get_wm_strut_unchecked(c, window):
    """
    Returns the struts for a window.

    This property is equivalent to a _NET_WM_STRUT_PARTIAL property where
    all start values are 0 and all end values are the height or width of
    the logical screen. _NET_WM_STRUT_PARTIAL was introduced later than
    _NET_WM_STRUT, however, so clients MAY set this property in addition to
    _NET_WM_STRUT_PARTIAL to ensure backward compatibility with Window
    Managers supporting older versions of the Specification.

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @return:        A strut dictionary.

                    Keys: left, right, top, bottom
    @rtype:         StrutCookie (CARDINAL[4]/32)
    """
    return StrutCookie(
        util.get_property_unchecked(c, window, atom(c, '_NET_WM_STRUT')))

def set_wm_strut(c, window, left, right, top, bottom):
    """
    Sets the struts for a window.

    This property is equivalent to a _NET_WM_STRUT_PARTIAL property where
    all start values are 0 and all end values are the height or width of
    the logical screen. _NET_WM_STRUT_PARTIAL was introduced later than
    _NET_WM_STRUT, however, so clients MAY set this property in addition to
    _NET_WM_STRUT_PARTIAL to ensure backward compatibility with Window
    Managers supporting older versions of the Specification.

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @param left:    Width of area at left side of screen.
    @type left:     CARDINAL/32
    @param right:   Width of area at right side of screen.
    @type right:    CARDINAL/32
    @param top:     Height of area at top side of screen.
    @type top:      CARDINAL/32
    @param bottom:  Height of area at bottom side of screen.
    @type bottom:   CARDINAL/32
    @rtype:         xcb.VoidCookie
    """
    packed = struct.pack('IIII', left, right, top, bottom)
    return c.core.ChangeProperty(xcb.xproto.PropMode.Replace, window,
                                 atom(c, '_NET_WM_STRUT'),
                                 CARDINAL, 32, 4,
                                 packed)

def set_wm_strut_checked(c, window, left, right, top, bottom):
    """
    Sets the struts for a window.

    This property is equivalent to a _NET_WM_STRUT_PARTIAL property where
    all start values are 0 and all end values are the height or width of
    the logical screen. _NET_WM_STRUT_PARTIAL was introduced later than
    _NET_WM_STRUT, however, so clients MAY set this property in addition to
    _NET_WM_STRUT_PARTIAL to ensure backward compatibility with Window
    Managers supporting older versions of the Specification.

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @param left:    Width of area at left side of screen.
    @type left:     CARDINAL/32
    @param right:   Width of area at right side of screen.
    @type right:    CARDINAL/32
    @param top:     Height of area at top side of screen.
    @type top:      CARDINAL/32
    @param bottom:  Height of area at bottom side of screen.
    @type bottom:   CARDINAL/32
    @rtype:         xcb.VoidCookie
    """
    packed = struct.pack('IIII', left, right, top, bottom)
    return c.core.ChangePropertyChecked(xcb.xproto.PropMode.Replace, window,
                                        atom(c, '_NET_WM_STRUT'),
                                        CARDINAL, 32, 4,
                                        packed)

# _NET_WM_STRUT_PARTIAL

class StrutPartialCookie(util.PropertyCookie):
    def reply(self):
        v = util.PropertyCookie.reply(self)

        if not v:
            return None

        return {
            'left': v[0],
            'right': v[1],
            'top': v[2],
            'bottom': v[3],
            'left_start_y': v[4],
            'left_end_y': v[5],
            'right_start_y': v[6],
            'right_end_y': v[7],
            'top_start_x': v[8],
            'top_end_x': v[9],
            'bottom_start_x': v[10],
            'bottom_end_x': v[11]
        }

def get_wm_strut_partial(c, window):
    """
    Returns the partial struts for a window.

    This property MUST be set by the Client if the window is to reserve
    space at the edge of the screen. The property contains 4 cardinals
    specifying the width of the reserved area at each border of the screen,
    and an additional 8 cardinals specifying the beginning and end
    corresponding to each of the four struts. The order of the values is
    left, right, top, bottom, left_start_y, left_end_y, right_start_y,
    right_end_y, top_start_x, top_end_x, bottom_start_x, bottom_end_x. All
    coordinates are root window coordinates. The client MAY change this
    property at any time, therefore the Window Manager MUST watch for
    property notify events if the Window Manager uses this property to
    assign special semantics to the window.

    If both this property and the _NET_WM_STRUT property are set, the Window
    Manager MUST ignore the _NET_WM_STRUT property values and use instead
    the values for _NET_WM_STRUT_PARTIAL. This will ensure that Clients can
    safely set both properties without giving up the improved semantics of
    the new property.

    The purpose of struts is to reserve space at the borders of the
    desktop. This is very useful for a docking area, a taskbar or a panel,
    for instance. The Window Manager should take this reserved area into
    account when constraining window positions - maximized windows, for
    example, should not cover that area.

    The start and end values associated with each strut allow areas to be
    reserved which do not span the entire width or height of the screen.
    Struts MUST be specified in root window coordinates, that is, they are
    not relative to the edges of any view port or Xinerama monitor.

    For example, for a panel-style Client appearing at the bottom of the
    screen, 50 pixels tall, and occupying the space from 200-600 pixels
    from the left of the screen edge would set a bottom strut of 50, and
    set bottom_start_x to 200 and bottom_end_x to 600. Another example is a
    panel on a screen using the Xinerama extension. Assume that the set up
    uses two monitors, one running at 1280x1024 and the other to the right
    running at 1024x768, with the top edge of the two physical displays
    aligned. If the panel wants to fill the entire bottom edge of the
    smaller display with a panel 50 pixels tall, it should set a bottom
    strut of 306, with bottom_start_x of 1280, and bottom_end_x of 2303.
    Note that the strut is relative to the screen edge, and not the edge of
    the xinerama monitor.

    Rationale: A simple "do not cover" hint is not enough for dealing with
    e.g. auto-hide panels.

    Notes: An auto-hide panel SHOULD set the strut to be its minimum,
    hidden size. A "corner" panel that does not extend for the full length
    of a screen border SHOULD only set one strut.

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @return:        A strut dictionary.

                    Keys: left, right, top, bottom, left_start_y, left_end_y,
                    right_start_y, right_end_y, top_start_x, top_end_x,
                    bottom_start_x, bottom_end_x
    @rtype:         StrutPartialCookie (CARDINAL[12]/32)
    """
    return StrutPartialCookie(
        util.get_property(c, window, atom(c, '_NET_WM_STRUT_PARTIAL')))

def get_wm_strut_partial_unchecked(c, window):
    """
    Returns the partial struts for a window.

    This property MUST be set by the Client if the window is to reserve
    space at the edge of the screen. The property contains 4 cardinals
    specifying the width of the reserved area at each border of the screen,
    and an additional 8 cardinals specifying the beginning and end
    corresponding to each of the four struts. The order of the values is
    left, right, top, bottom, left_start_y, left_end_y, right_start_y,
    right_end_y, top_start_x, top_end_x, bottom_start_x, bottom_end_x. All
    coordinates are root window coordinates. The client MAY change this
    property at any time, therefore the Window Manager MUST watch for
    property notify events if the Window Manager uses this property to
    assign special semantics to the window.

    If both this property and the _NET_WM_STRUT property are set, the Window
    Manager MUST ignore the _NET_WM_STRUT property values and use instead
    the values for _NET_WM_STRUT_PARTIAL. This will ensure that Clients can
    safely set both properties without giving up the improved semantics of
    the new property.

    The purpose of struts is to reserve space at the borders of the
    desktop. This is very useful for a docking area, a taskbar or a panel,
    for instance. The Window Manager should take this reserved area into
    account when constraining window positions - maximized windows, for
    example, should not cover that area.

    The start and end values associated with each strut allow areas to be
    reserved which do not span the entire width or height of the screen.
    Struts MUST be specified in root window coordinates, that is, they are
    not relative to the edges of any view port or Xinerama monitor.

    For example, for a panel-style Client appearing at the bottom of the
    screen, 50 pixels tall, and occupying the space from 200-600 pixels
    from the left of the screen edge would set a bottom strut of 50, and
    set bottom_start_x to 200 and bottom_end_x to 600. Another example is a
    panel on a screen using the Xinerama extension. Assume that the set up
    uses two monitors, one running at 1280x1024 and the other to the right
    running at 1024x768, with the top edge of the two physical displays
    aligned. If the panel wants to fill the entire bottom edge of the
    smaller display with a panel 50 pixels tall, it should set a bottom
    strut of 306, with bottom_start_x of 1280, and bottom_end_x of 2303.
    Note that the strut is relative to the screen edge, and not the edge of
    the xinerama monitor.

    Rationale: A simple "do not cover" hint is not enough for dealing with
    e.g. auto-hide panels.

    Notes: An auto-hide panel SHOULD set the strut to be its minimum,
    hidden size. A "corner" panel that does not extend for the full length
    of a screen border SHOULD only set one strut.

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @return:        A strut dictionary.

                    Keys: left, right, top, bottom, left_start_y, left_end_y,
                    right_start_y, right_end_y, top_start_x, top_end_x,
                    bottom_start_x, bottom_end_x
    @rtype:         StrutPartialCookie (CARDINAL[12]/32)
    """
    return StrutPartialCookie(
        util.get_property_unchecked(c, window,
                                    atom(c, '_NET_WM_STRUT_PARTIAL')))

def set_wm_strut_partial(c, window, left, right, top, bottom, left_start_y,
                         left_end_y, right_start_y, right_end_y, top_start_x,
                         top_end_x, bottom_start_x, bottom_end_x):
    """
    Sets the partial struts for a window.

    This property MUST be set by the Client if the window is to reserve
    space at the edge of the screen. The property contains 4 cardinals
    specifying the width of the reserved area at each border of the screen,
    and an additional 8 cardinals specifying the beginning and end
    corresponding to each of the four struts. The order of the values is
    left, right, top, bottom, left_start_y, left_end_y, right_start_y,
    right_end_y, top_start_x, top_end_x, bottom_start_x, bottom_end_x. All
    coordinates are root window coordinates. The client MAY change this
    property at any time, therefore the Window Manager MUST watch for
    property notify events if the Window Manager uses this property to
    assign special semantics to the window.

    If both this property and the _NET_WM_STRUT property are set, the Window
    Manager MUST ignore the _NET_WM_STRUT property values and use instead
    the values for _NET_WM_STRUT_PARTIAL. This will ensure that Clients can
    safely set both properties without giving up the improved semantics of
    the new property.

    The purpose of struts is to reserve space at the borders of the
    desktop. This is very useful for a docking area, a taskbar or a panel,
    for instance. The Window Manager should take this reserved area into
    account when constraining window positions - maximized windows, for
    example, should not cover that area.

    The start and end values associated with each strut allow areas to be
    reserved which do not span the entire width or height of the screen.
    Struts MUST be specified in root window coordinates, that is, they are
    not relative to the edges of any view port or Xinerama monitor.

    For example, for a panel-style Client appearing at the bottom of the
    screen, 50 pixels tall, and occupying the space from 200-600 pixels
    from the left of the screen edge would set a bottom strut of 50, and
    set bottom_start_x to 200 and bottom_end_x to 600. Another example is a
    panel on a screen using the Xinerama extension. Assume that the set up
    uses two monitors, one running at 1280x1024 and the other to the right
    running at 1024x768, with the top edge of the two physical displays
    aligned. If the panel wants to fill the entire bottom edge of the
    smaller display with a panel 50 pixels tall, it should set a bottom
    strut of 306, with bottom_start_x of 1280, and bottom_end_x of 2303.
    Note that the strut is relative to the screen edge, and not the edge of
    the xinerama monitor.

    Rationale: A simple "do not cover" hint is not enough for dealing with
    e.g. auto-hide panels.

    Notes: An auto-hide panel SHOULD set the strut to be its minimum,
    hidden size. A "corner" panel that does not extend for the full length
    of a screen border SHOULD only set one strut.

    @param c:               An xpyb connection object.
    @param window:          A window identifier.
    @param left:            Width of area at left side of screen.
    @type left:             CARDINAL/32
    @param right:           Width of area at right side of screen.
    @type right:            CARDINAL/32
    @param top:             Height of area at top side of screen.
    @type top:              CARDINAL/32
    @param bottom:          Height of area at bottom side of screen.
    @type bottom:           CARDINAL/32
    @param left_start_y:
    @param left_end_y:
    @param right_start_y:
    @param right_end_y:
    @param top_start_x:
    @param top_end_x:
    @param bottom_start_x:
    @param bottom_end_x:
    @rtype:                 xcb.VoidCookie
    """
    packed = struct.pack('I' * 12, left, right, top, bottom, left_start_y,
                         left_end_y, right_start_y, right_end_y, top_start_x,
                         top_end_x, bottom_start_x, bottom_end_x)
    return c.core.ChangeProperty(xcb.xproto.PropMode.Replace, window,
                                 atom(c, '_NET_WM_STRUT_PARTIAL'),
                                 CARDINAL, 32, 12,
                                 packed)

def set_wm_strut_partial_checked(c, window, left, right, top, bottom,
                                 left_start_y, left_end_y, right_start_y,
                                 right_end_y, top_start_x, top_end_x,
                                 bottom_start_x, bottom_end_x):
    """
    Sets the partial struts for a window.

    This property MUST be set by the Client if the window is to reserve
    space at the edge of the screen. The property contains 4 cardinals
    specifying the width of the reserved area at each border of the screen,
    and an additional 8 cardinals specifying the beginning and end
    corresponding to each of the four struts. The order of the values is
    left, right, top, bottom, left_start_y, left_end_y, right_start_y,
    right_end_y, top_start_x, top_end_x, bottom_start_x, bottom_end_x. All
    coordinates are root window coordinates. The client MAY change this
    property at any time, therefore the Window Manager MUST watch for
    property notify events if the Window Manager uses this property to
    assign special semantics to the window.

    If both this property and the _NET_WM_STRUT property are set, the Window
    Manager MUST ignore the _NET_WM_STRUT property values and use instead
    the values for _NET_WM_STRUT_PARTIAL. This will ensure that Clients can
    safely set both properties without giving up the improved semantics of
    the new property.

    The purpose of struts is to reserve space at the borders of the
    desktop. This is very useful for a docking area, a taskbar or a panel,
    for instance. The Window Manager should take this reserved area into
    account when constraining window positions - maximized windows, for
    example, should not cover that area.

    The start and end values associated with each strut allow areas to be
    reserved which do not span the entire width or height of the screen.
    Struts MUST be specified in root window coordinates, that is, they are
    not relative to the edges of any view port or Xinerama monitor.

    For example, for a panel-style Client appearing at the bottom of the
    screen, 50 pixels tall, and occupying the space from 200-600 pixels
    from the left of the screen edge would set a bottom strut of 50, and
    set bottom_start_x to 200 and bottom_end_x to 600. Another example is a
    panel on a screen using the Xinerama extension. Assume that the set up
    uses two monitors, one running at 1280x1024 and the other to the right
    running at 1024x768, with the top edge of the two physical displays
    aligned. If the panel wants to fill the entire bottom edge of the
    smaller display with a panel 50 pixels tall, it should set a bottom
    strut of 306, with bottom_start_x of 1280, and bottom_end_x of 2303.
    Note that the strut is relative to the screen edge, and not the edge of
    the xinerama monitor.

    Rationale: A simple "do not cover" hint is not enough for dealing with
    e.g. auto-hide panels.

    Notes: An auto-hide panel SHOULD set the strut to be its minimum,
    hidden size. A "corner" panel that does not extend for the full length
    of a screen border SHOULD only set one strut.

    @param c:               An xpyb connection object.
    @param window:          A window identifier.
    @param left:            Width of area at left side of screen.
    @type left:             CARDINAL/32
    @param right:           Width of area at right side of screen.
    @type right:            CARDINAL/32
    @param top:             Height of area at top side of screen.
    @type top:              CARDINAL/32
    @param bottom:          Height of area at bottom side of screen.
    @type bottom:           CARDINAL/32
    @param left_start_y:
    @param left_end_y:
    @param right_start_y:
    @param right_end_y:
    @param top_start_x:
    @param top_end_x:
    @param bottom_start_x:
    @param bottom_end_x:
    @rtype:                 xcb.VoidCookie
    """
    packed = struct.pack('I' * 12, left, right, top, bottom, left_start_y,
                         left_end_y, right_start_y, right_end_y, top_start_x,
                         top_end_x, bottom_start_x, bottom_end_x)
    return c.core.ChangePropertyChecked(xcb.xproto.PropMode.Replace, window,
                                        atom(c, '_NET_WM_STRUT_PARTIAL'),
                                        CARDINAL, 32, 12,
                                        packed)

# _NET_WM_ICON_GEOMETRY

class IconGeometryCookie(util.PropertyCookie):
    def reply(self):
        v = util.PropertyCookie.reply(self)

        if not v:
            return None

        return {
            'x': v[0],
            'y': v[1],
            'width': v[2],
            'height': v[3]
        }

def get_wm_icon_geometry(c, window):
    """
    Returns the icon geometry for a window.

    This optional property MAY be set by stand alone tools like a taskbar
    or an iconbox. It specifies the geometry of a possible icon in case the
    window is iconified.

    Rationale: This makes it possible for a Window Manager to display a
    nice animation like morphing the window into its icon.

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @return:        An icon geometry dictionary.

                    Keys: x, y, width, height
    @rtype:         IconGeometryCookie (CARDINAL[4]/32)
    """
    return IconGeometryCookie(
        util.get_property(c, window, atom(c, '_NET_WM_ICON_GEOMETRY')))

def get_wm_icon_geometry_unchecked(c, window):
    """
    Returns the icon geometry for a window.

    This optional property MAY be set by stand alone tools like a taskbar
    or an iconbox. It specifies the geometry of a possible icon in case the
    window is iconified.

    Rationale: This makes it possible for a Window Manager to display a
    nice animation like morphing the window into its icon.

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @return:        An icon geometry dictionary.

                    Keys: x, y, width, height
    @rtype:         IconGeometryCookie (CARDINAL[4]/32)
    """
    return IconGeometryCookie(
        util.get_property_unchecked(c, window,
                                    atom(c, '_NET_WM_ICON_GEOMETRY')))

def set_wm_icon_geometry(c, window, x, y, width, height):
    """
    Sets the icon geometry for a window.

    This optional property MAY be set by stand alone tools like a taskbar
    or an iconbox. It specifies the geometry of a possible icon in case the
    window is iconified.

    Rationale: This makes it possible for a Window Manager to display a
    nice animation like morphing the window into its icon.

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @param x:       x coordinate of icon area.
    @type x:        CARDINAL/32
    @param y:       y coordinate of icon area.
    @type y:        CARDINAL/32
    @param width:   Width of icon area.
    @type width:    CARDINAL/32
    @param height:  Height of icon area.
    @type height:   CARDINAL/32
    @rtype:         xcb.VoidCookie
    """
    packed = struct.pack('IIII', x, y, width, height)
    return c.core.ChangeProperty(xcb.xproto.PropMode.Replace, window,
                                 atom(c, '_NET_WM_ICON_GEOMETRY'),
                                 CARDINAL, 32, 4,
                                 packed)

def set_wm_icon_geometry_checked(c, window, x, y, width, height):
    """
    Sets the icon geometry for a window.

    This optional property MAY be set by stand alone tools like a taskbar
    or an iconbox. It specifies the geometry of a possible icon in case the
    window is iconified.

    Rationale: This makes it possible for a Window Manager to display a
    nice animation like morphing the window into its icon.

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @param x:       x coordinate of icon area.
    @type x:        CARDINAL/32
    @param y:       y coordinate of icon area.
    @type y:        CARDINAL/32
    @param width:   Width of icon area.
    @type width:    CARDINAL/32
    @param height:  Height of icon area.
    @type height:   CARDINAL/32
    @rtype:         xcb.VoidCookie
    """
    packed = struct.pack('IIII', x, y, width, height)
    return c.core.ChangePropertyChecked(xcb.xproto.PropMode.Replace, window,
                                        atom(c, '_NET_WM_ICON_GEOMETRY'),
                                        CARDINAL, 32, 4,
                                        packed)

# _NET_WM_ICON

class IconCookie(util.PropertyCookie):
    def reply(self):
        v = util.PropertyCookie.reply(self)

        if not v:
            return None

        ret = []
        start = 0
        while start < len(v):
            w, h = v[start], v[start + 1]
            upto = w * h

            ret.append({
                'width': w,
                'height': h,
                'data': v[start + 2:start + upto + 2]
            })

            start = start + upto + 2

        return ret

def get_wm_icon(c, window):
    """
    Returns an array of possible icons for a window.

    This is an array of possible icons for the client. This specification
    does not stipulate what size these icons should be, but individual
    desktop environments or toolkits may do so. The Window Manager MAY
    scale any of these icons to an appropriate size.

    This is an array of 32bit packed CARDINAL ARGB with high byte being A,
    low byte being B. The first two cardinals are width, height. Data is in
    rows, left to right and top to bottom.

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @return:        A list of icon dictionaries.

                    Keys: width, height, data
    @rtype:         IconCookie (CARDINAL[][2+n]/32)
    """
    return IconCookie(
        util.get_property(c, window, atom(c, '_NET_WM_ICON')))

def get_wm_icon_unchecked(c, window):
    """
    Returns an array of possible icons for a window.

    This is an array of possible icons for the client. This specification
    does not stipulate what size these icons should be, but individual
    desktop environments or toolkits may do so. The Window Manager MAY
    scale any of these icons to an appropriate size.

    This is an array of 32bit packed CARDINAL ARGB with high byte being A,
    low byte being B. The first two cardinals are width, height. Data is in
    rows, left to right and top to bottom.

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @return:        A list of icon dictionaries.

                    Keys: width, height, data
    @rtype:         IconCookie (CARDINAL[][2+n]/32)
    """
    return IconCookie(
        util.get_property_unchecked(c, window,
                                    atom(c, '_NET_WM_ICON')))

def set_wm_icon(c, window, icons):
    """
    Sets the array of possible icons for a window.

    This is an array of possible icons for the client. This specification
    does not stipulate what size these icons should be, but individual
    desktop environments or toolkits may do so. The Window Manager MAY
    scale any of these icons to an appropriate size.

    This is an array of 32bit packed CARDINAL ARGB with high byte being A,
    low byte being B. The first two cardinals are width, height. Data is in
    rows, left to right and top to bottom.

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @param icons:   A list icon dictionaries. Each dictionary should have
                    the following keys: width, height and data.
    @type icons:    CARDINAL[][2+n]/32
    @rtype:         xcb.VoidCookie
    """
    flatten = []
    for icon in icons:
        flatten.append(icon['width'])
        flatten.append(icon['height'])
        for argb in icon['data']:
            flatten.append(argb)
    packed = struct.pack('I' * len(flatten), *flatten)

    return c.core.ChangeProperty(xcb.xproto.PropMode.Replace, window,
                                 atom(c, '_NET_WM_ICON'),
                                 CARDINAL, 32, len(flatten),
                                 packed)

def set_wm_icon_checked(c, window, icons):
    """
    Sets the array of possible icons for a window.

    This is an array of possible icons for the client. This specification
    does not stipulate what size these icons should be, but individual
    desktop environments or toolkits may do so. The Window Manager MAY
    scale any of these icons to an appropriate size.

    This is an array of 32bit packed CARDINAL ARGB with high byte being A,
    low byte being B. The first two cardinals are width, height. Data is in
    rows, left to right and top to bottom.

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @param icons:   A list of possible icons. Each list should start with
                    the width and height of the icon data following.
    @type icons:    CARDINAL[][2+n]/32
    @rtype:         xcb.VoidCookie
    """
    flatten = []
    for icon in icons:
        flatten.append(icon['width'])
        flatten.append(icon['height'])
        for argb in icon['data']:
            flatten.append(argb)
    packed = struct.pack('I' * len(flatten), *flatten)

    return c.core.ChangePropertyChecked(xcb.xproto.PropMode.Replace, window,
                                        atom(c, '_NET_WM_ICON'),
                                        CARDINAL, 32, len(flatten),
                                        packed)

# _NET_WM_PID

def get_wm_pid(c, window):
    """
    Get the process ID of the client owning a window.

    If set, this property MUST contain the process ID of the client owning
    this window. This MAY be used by the Window Manager to kill windows
    which do not respond to the _NET_WM_PING protocol.

    If _NET_WM_PID is set, the ICCCM-specified property WM_CLIENT_MACHINE
    MUST also be set. While the ICCCM only requests that WM_CLIENT_MACHINE
    is set "to a string that forms the name of the machine running the
    client as seen from the machine running the server" conformance to this
    specification requires that WM_CLIENT_MACHINE be set to the
    fully-qualified domain name of the client's host.

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @return:        The window's client's process ID.
    @rtype:         util.PropertyCookieSingle (CARDINAL/32)
    """
    return util.PropertyCookieSingle(
        util.get_property(c, window, atom(c, '_NET_WM_PID')))

def get_wm_pid_unchecked(c, window):
    """
    Get the process ID of the client owning a window.

    If set, this property MUST contain the process ID of the client owning
    this window. This MAY be used by the Window Manager to kill windows
    which do not respond to the _NET_WM_PING protocol.

    If _NET_WM_PID is set, the ICCCM-specified property WM_CLIENT_MACHINE
    MUST also be set. While the ICCCM only requests that WM_CLIENT_MACHINE
    is set "to a string that forms the name of the machine running the
    client as seen from the machine running the server" conformance to this
    specification requires that WM_CLIENT_MACHINE be set to the
    fully-qualified domain name of the client's host.

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @return:        The window's client's process ID.
    @rtype:         util.PropertyCookieSingle (CARDINAL/32)
    """
    return util.PropertyCookieSingle(
        util.get_property_unchecked(c, window, atom(c, '_NET_WM_PID')))

def set_wm_pid(c, window, pid):
    """
    Sets the process ID of the client owning a window.

    If set, this property MUST contain the process ID of the client owning
    this window. This MAY be used by the Window Manager to kill windows
    which do not respond to the _NET_WM_PING protocol.

    If _NET_WM_PID is set, the ICCCM-specified property WM_CLIENT_MACHINE
    MUST also be set. While the ICCCM only requests that WM_CLIENT_MACHINE
    is set "to a string that forms the name of the machine running the
    client as seen from the machine running the server" conformance to this
    specification requires that WM_CLIENT_MACHINE be set to the
    fully-qualified domain name of the client's host.

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @param pid:     A process ID.
    @type pid:      CARDINAL/32
    @rtype:         xcb.VoidCookie
    """
    return c.core.ChangeProperty(xcb.xproto.PropMode.Replace, window,
                                 atom(c, '_NET_WM_PID'),
                                 CARDINAL, 32, 1,
                                 [pid])

def set_wm_pid_checked(c, window, pid):
    """
    Sets the process ID of the client owning a window.

    If set, this property MUST contain the process ID of the client owning
    this window. This MAY be used by the Window Manager to kill windows
    which do not respond to the _NET_WM_PING protocol.

    If _NET_WM_PID is set, the ICCCM-specified property WM_CLIENT_MACHINE
    MUST also be set. While the ICCCM only requests that WM_CLIENT_MACHINE
    is set "to a string that forms the name of the machine running the
    client as seen from the machine running the server" conformance to this
    specification requires that WM_CLIENT_MACHINE be set to the
    fully-qualified domain name of the client's host.

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @param pid:     A process ID.
    @type pid:      CARDINAL/32
    @rtype:         xcb.VoidCookie
    """
    return c.core.ChangePropertyChecked(xcb.xproto.PropMode.Replace, window,
                                        atom(c, '_NET_WM_PID'),
                                        CARDINAL, 32, 1,
                                        [pid])

# _NET_WM_HANDLED_ICONS

def get_wm_handled_icons(c, window):
    """
    Gets the "handled icons" property.

    This property can be set by a Pager on one of its own toplevel windows
    to indicate that the Window Manager need not provide icons for
    iconified windows, for example if it is a taskbar and provides buttons
    for iconified windows.

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @return:        Whether this property is set or not.
    @rtype:         util.PropertyCookieSingle (CARDINAL/32)
    """
    return util.PropertyCookieSingle(
        util.get_property(c, window, atom(c, '_NET_WM_HANDLED_ICONS')))

def get_wm_handled_icons_unchecked(c, window):
    """
    Gets the "handled icons" property.

    This property can be set by a Pager on one of its own toplevel windows
    to indicate that the Window Manager need not provide icons for
    iconified windows, for example if it is a taskbar and provides buttons
    for iconified windows.

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @return:        Whether this property is set or not.
    @rtype:         util.PropertyCookieSingle (CARDINAL/32)
    """
    return util.PropertyCookieSingle(
        util.get_property_unchecked(c, window,
                                    atom(c, '_NET_WM_HANDLED_ICONS')))

def set_wm_handled_icons(c, window):
    """
    Sets the "handled icons" property.

    This property can be set by a Pager on one of its own toplevel windows
    to indicate that the Window Manager need not provide icons for
    iconified windows, for example if it is a taskbar and provides buttons
    for iconified windows.

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @return:        Whether this property is set or not.
    @rtype:         xcb.VoidCookie
    """
    return c.core.ChangeProperty(xcb.xproto.PropMode.Replace, window,
                                 atom(c, '_NET_WM_HANDLED_ICONS'),
                                 CARDINAL, 32, 1,
                                 [1])

def set_wm_handled_icons_checked(c, window):
    """
    Sets the "handled icons" property.

    This property can be set by a Pager on one of its own toplevel windows
    to indicate that the Window Manager need not provide icons for
    iconified windows, for example if it is a taskbar and provides buttons
    for iconified windows.

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @return:        Whether this property is set or not.
    @rtype:         xcb.VoidCookie
    """
    return c.core.ChangePropertyChecked(xcb.xproto.PropMode.Replace, window,
                                        atom(c, '_NET_WM_HANDLED_ICONS'),
                                        CARDINAL, 32, 1,
                                        [1])

# _NET_WM_USER_TIME

def get_wm_user_time(c, window):
    """
    Get the time at which the last user activity occurred on a window.

    Clients should set this property on every new toplevel window (or on
    the window pointed out by the _NET_WM_USER_TIME_WINDOW property),
    before mapping the window, to the timestamp of the user interaction
    that caused the window to appear. A client that only deals with core
    events, might, for example, use the timestamp of the last KeyPress or
    ButtonPress event. ButtonRelease and KeyRelease events should not
    generally be considered to be user interaction, because an application
    may receive KeyRelease events from global keybindings, and generally
    release events may have later timestamp than actions that were
    triggered by the matching press events. Clients can obtain the
    timestamp that caused its first window to appear from the
    DESKTOP_STARTUP_ID environment variable, if the app was launched with
    startup notification. If the client does not know the timestamp of the
    user interaction that caused the first window to appear (e.g. because
    it was not launched with startup notification), then it should not set
    the property for that window. The special value of zero on a newly
    mapped window can be used to request that the window not be initially
    focused when it is mapped.

    If the client has the active window, it should also update this
    property on the window whenever there's user activity.

    Rationale: This property allows a Window Manager to alter the focus,
    stacking, and/or placement behavior of windows when they are mapped
    depending on whether the new window was created by a user action or is
    a "pop-up" window activated by a timer or some other event.

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @return:        The XServer time when user activity last occurred.
    @rtype:         util.PropertyCookieSingle (CARDINAL/32)
    """
    return util.PropertyCookieSingle(
        util.get_property(c, window, atom(c, '_NET_WM_USER_TIME')))

def get_wm_user_time_unchecked(c, window):
    """
    Get the time at which the last user activity occurred on a window.

    Clients should set this property on every new toplevel window (or on
    the window pointed out by the _NET_WM_USER_TIME_WINDOW property),
    before mapping the window, to the timestamp of the user interaction
    that caused the window to appear. A client that only deals with core
    events, might, for example, use the timestamp of the last KeyPress or
    ButtonPress event. ButtonRelease and KeyRelease events should not
    generally be considered to be user interaction, because an application
    may receive KeyRelease events from global keybindings, and generally
    release events may have later timestamp than actions that were
    triggered by the matching press events. Clients can obtain the
    timestamp that caused its first window to appear from the
    DESKTOP_STARTUP_ID environment variable, if the app was launched with
    startup notification. If the client does not know the timestamp of the
    user interaction that caused the first window to appear (e.g. because
    it was not launched with startup notification), then it should not set
    the property for that window. The special value of zero on a newly
    mapped window can be used to request that the window not be initially
    focused when it is mapped.

    If the client has the active window, it should also update this
    property on the window whenever there's user activity.

    Rationale: This property allows a Window Manager to alter the focus,
    stacking, and/or placement behavior of windows when they are mapped
    depending on whether the new window was created by a user action or is
    a "pop-up" window activated by a timer or some other event.

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @return:        The XServer time when user activity last occurred.
    @rtype:         util.PropertyCookieSingle (CARDINAL/32)
    """
    return util.PropertyCookieSingle(
        util.get_property_unchecked(c, window, atom(c, '_NET_WM_USER_TIME')))

def set_wm_user_time(c, window, user_time):
    """
    Sets the time that user activity last occurred on this window.

    Clients should set this property on every new toplevel window (or on
    the window pointed out by the _NET_WM_USER_TIME_WINDOW property),
    before mapping the window, to the timestamp of the user interaction
    that caused the window to appear. A client that only deals with core
    events, might, for example, use the timestamp of the last KeyPress or
    ButtonPress event. ButtonRelease and KeyRelease events should not
    generally be considered to be user interaction, because an application
    may receive KeyRelease events from global keybindings, and generally
    release events may have later timestamp than actions that were
    triggered by the matching press events. Clients can obtain the
    timestamp that caused its first window to appear from the
    DESKTOP_STARTUP_ID environment variable, if the app was launched with
    startup notification. If the client does not know the timestamp of the
    user interaction that caused the first window to appear (e.g. because
    it was not launched with startup notification), then it should not set
    the property for that window. The special value of zero on a newly
    mapped window can be used to request that the window not be initially
    focused when it is mapped.

    If the client has the active window, it should also update this
    property on the window whenever there's user activity.

    Rationale: This property allows a Window Manager to alter the focus,
    stacking, and/or placement behavior of windows when they are mapped
    depending on whether the new window was created by a user action or is
    a "pop-up" window activated by a timer or some other event.

    @param c:           An xpyb connection object.
    @param window:      A window identifier.
    @param user_time:   Last user activity time.
    @type user_time:    CARDINAL/32
    @rtype:             xcb.VoidCookie
    """
    return c.core.ChangeProperty(xcb.xproto.PropMode.Replace, window,
                                 atom(c, '_NET_WM_USER_TIME'),
                                 CARDINAL, 32, 1,
                                 [user_time])

def set_wm_user_time_checked(c, window, user_time):
    """
    Sets the time that user activity last occurred on this window.

    Clients should set this property on every new toplevel window (or on
    the window pointed out by the _NET_WM_USER_TIME_WINDOW property),
    before mapping the window, to the timestamp of the user interaction
    that caused the window to appear. A client that only deals with core
    events, might, for example, use the timestamp of the last KeyPress or
    ButtonPress event. ButtonRelease and KeyRelease events should not
    generally be considered to be user interaction, because an application
    may receive KeyRelease events from global keybindings, and generally
    release events may have later timestamp than actions that were
    triggered by the matching press events. Clients can obtain the
    timestamp that caused its first window to appear from the
    DESKTOP_STARTUP_ID environment variable, if the app was launched with
    startup notification. If the client does not know the timestamp of the
    user interaction that caused the first window to appear (e.g. because
    it was not launched with startup notification), then it should not set
    the property for that window. The special value of zero on a newly
    mapped window can be used to request that the window not be initially
    focused when it is mapped.

    If the client has the active window, it should also update this
    property on the window whenever there's user activity.

    Rationale: This property allows a Window Manager to alter the focus,
    stacking, and/or placement behavior of windows when they are mapped
    depending on whether the new window was created by a user action or is
    a "pop-up" window activated by a timer or some other event.

    @param c:           An xpyb connection object.
    @param window:      A window identifier.
    @param user_time:   Last user activity time.
    @type user_time:    CARDINAL/32
    @rtype:             xcb.VoidCookie
    """
    return c.core.ChangePropertyChecked(xcb.xproto.PropMode.Replace, window,
                                        atom(c, '_NET_WM_USER_TIME'),
                                        CARDINAL, 32, 1,
                                        [user_time])

# _NET_WM_USER_TIME_WINDOW

def get_wm_user_time_window(c, window):
    """
    Gets the window that sets the _NET_WM_USER_TIME property.

    This property contains the XID of a window on which the client sets the
    _NET_WM_USER_TIME property. Clients should check whether the window
    manager supports _NET_WM_USER_TIME_WINDOW and fall back to setting the
    _NET_WM_USER_TIME property on the toplevel window if it doesn't.

    Rationale: Storing the frequently changing _NET_WM_USER_TIME property
    on the toplevel window itself causes every application that is
    interested in any of the properties of that window to be woken up on
    every keypress, which is particularly bad for laptops running on
    battery power.

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @return:        Window identifier that sets the _NET_WM_USER_TIME property.
    @rtype:         util.PropertyCookieSingle (WINDOW/32)
    """
    return util.PropertyCookieSingle(
        util.get_property(c, window, atom(c, '_NET_WM_USER_TIME_WINDOW')))

def get_wm_user_time_window_unchecked(c, window):
    """
    Gets the window that sets the _NET_WM_USER_TIME property.

    This property contains the XID of a window on which the client sets the
    _NET_WM_USER_TIME property. Clients should check whether the window
    manager supports _NET_WM_USER_TIME_WINDOW and fall back to setting the
    _NET_WM_USER_TIME property on the toplevel window if it doesn't.

    Rationale: Storing the frequently changing _NET_WM_USER_TIME property
    on the toplevel window itself causes every application that is
    interested in any of the properties of that window to be woken up on
    every keypress, which is particularly bad for laptops running on
    battery power.

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @return:        Window identifier that sets the _NET_WM_USER_TIME property.
    @rtype:         util.PropertyCookieSingle (WINDOW/32)
    """
    return util.PropertyCookieSingle(
        util.get_property_unchecked(c, window,
                                    atom(c, '_NET_WM_USER_TIME_WINDOW')))

def set_wm_user_time_window(c, window, time_win):
    """
    Sets the window identifier that sets the _NET_WM_USER_TIME property.

    This property contains the XID of a window on which the client sets the
    _NET_WM_USER_TIME property. Clients should check whether the window
    manager supports _NET_WM_USER_TIME_WINDOW and fall back to setting the
    _NET_WM_USER_TIME property on the toplevel window if it doesn't.

    Rationale: Storing the frequently changing _NET_WM_USER_TIME property
    on the toplevel window itself causes every application that is
    interested in any of the properties of that window to be woken up on
    every keypress, which is particularly bad for laptops running on
    battery power.

    @param c:           An xpyb connection object.
    @param window:      A window identifier.
    @param time_win:    Window ID that sets the _NET_WM_USER_TIME property.
    @type time_win:     WINDOW/32
    @rtype:             xcb.VoidCookie
    """
    return c.core.ChangeProperty(xcb.xproto.PropMode.Replace, window,
                                 atom(c, '_NET_WM_USER_TIME_WINDOW'),
                                 xcb.xproto.Atom.WINDOW, 32, 1,
                                 [time_win])

def set_wm_user_time_window_checked(c, window, time_win):
    """
    Sets the window identifier that sets the _NET_WM_USER_TIME property.

    This property contains the XID of a window on which the client sets the
    _NET_WM_USER_TIME property. Clients should check whether the window
    manager supports _NET_WM_USER_TIME_WINDOW and fall back to setting the
    _NET_WM_USER_TIME property on the toplevel window if it doesn't.

    Rationale: Storing the frequently changing _NET_WM_USER_TIME property
    on the toplevel window itself causes every application that is
    interested in any of the properties of that window to be woken up on
    every keypress, which is particularly bad for laptops running on
    battery power.

    @param c:           An xpyb connection object.
    @param window:      A window identifier.
    @param time_win:    Window ID that sets the _NET_WM_USER_TIME property.
    @type time_win:     WINDOW/32
    @rtype:             xcb.VoidCookie
    """
    return c.core.ChangePropertyChecked(xcb.xproto.PropMode.Replace, window,
                                        atom(c, '_NET_WM_USER_TIME_WINDOW'),
                                        xcb.xproto.Atom.WINDOW, 32, 1,
                                        [time_win])

# _NET_FRAME_EXTENTS

class FrameExtentsCookie(util.PropertyCookie):
    def reply(self):
        v = util.PropertyCookie.reply(self)

        if not v:
            return None

        return {
            'left': v[0],
            'right': v[1],
            'top': v[2],
            'bottom': v[3]
        }

def get_frame_extents(c, window):
    """
    Returns the frame extents for a window.

    The Window Manager MUST set _NET_FRAME_EXTENTS to the extents of the
    window's frame. left, right, top and bottom are widths of the
    respective borders added by the Window Manager.

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @return:        A frame extents dictionary.

                    Keys: left, right, top, bottom
    @rtype:         FrameExtentsCookie (CARDINAL[4]/32)
    """
    return FrameExtentsCookie(
        util.get_property(c, window, atom(c, '_NET_FRAME_EXTENTS')))

def get_frame_extents_unchecked(c, window):
    """
    Returns the frame extents for a window.

    The Window Manager MUST set _NET_FRAME_EXTENTS to the extents of the
    window's frame. left, right, top and bottom are widths of the
    respective borders added by the Window Manager.

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @return:        A frame extents dictionary.

                    Keys: left, right, top, bottom
    @rtype:         FrameExtentsCookie (CARDINAL[4]/32)
    """
    return FrameExtentsCookie(
        util.get_property_unchecked(c, window,
                                    atom(c, '_NET_FRAME_EXTENTS')))

def set_frame_extents(c, window, left, right, top, bottom):
    """
    Sets the frame extents for a window.

    The Window Manager MUST set _NET_FRAME_EXTENTS to the extents of the
    window's frame. left, right, top and bottom are widths of the
    respective borders added by the Window Manager.

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @param left:    Width of left border.
    @type left:     CARDINAL/32
    @param right:   Width of right border.
    @type right:    CARDINAL/32
    @param top:     Height of top border.
    @type top:      CARDINAL/32
    @param bottom:  Height of bottom border.
    @type bottom:   CARDINAL/32
    @rtype:         xcb.VoidCookie
    """
    packed = struct.pack('IIII', left, right, top, bottom)
    return c.core.ChangeProperty(xcb.xproto.PropMode.Replace, window,
                                 atom(c, '_NET_FRAME_EXTENTS'),
                                 CARDINAL, 32, 4,
                                 packed)

def set_frame_extents_checked(c, window, left, right, top, bottom):
    """
    Sets the frame extents for a window.

    The Window Manager MUST set _NET_FRAME_EXTENTS to the extents of the
    window's frame. left, right, top and bottom are widths of the
    respective borders added by the Window Manager.

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @param left:    Width of left border.
    @type left:     CARDINAL/32
    @param right:   Width of right border.
    @type right:    CARDINAL/32
    @param top:     Height of top border.
    @type top:      CARDINAL/32
    @param bottom:  Height of bottom border.
    @type bottom:   CARDINAL/32
    @rtype:         xcb.VoidCookie
    """
    packed = struct.pack('IIII', left, right, top, bottom)
    return c.core.ChangePropertyChecked(xcb.xproto.PropMode.Replace, window,
                                        atom(c, '_NET_FRAME_EXTENTS'),
                                        CARDINAL, 32, 4,
                                        packed)

# _NET_WM_PING

def request_wm_ping(c, window, response=False,
                    timestamp=xcb.xproto.Time.CurrentTime):
    """
    Sends an event to root window to ping a window or respond to a ping.

    This protocol allows the Window Manager to determine if the Client is
    still processing X events. This can be used by the Window Manager to
    determine if a window which fails to close after being sent
    WM_DELETE_WINDOW has stopped responding or has stalled for some other
    reason, such as waiting for user confirmation. A Client SHOULD indicate
    that it is willing to participate in this protocol by listing
    _NET_WM_PING in the WM_PROTOCOLS property of the client window.

    A participating Client receiving this message MUST send it back to the
    root window immediately, by setting window = root, and calling
    XSendEvent with the same event mask like all other root window messages
    in this specification use. The Client MUST NOT alter any field in the
    event other than the window. This includes all 5 longs in the data.l[5]
    array. The Window Manager can uniquely identify the ping by the
    timestamp and the data.l[2] field if necessary. Note that some older
    clients may not preserve data.l[2] through data.l[4].

    The Window Manager MAY kill the Client (using _NET_WM_PID) if it fails
    to respond to this protocol within a reasonable time.

    @param c:           An xpyb connection object.
    @param window:      A window identifier.
    @param response:    Whether this is a response to a ping request or not.
    @type timestamp:    Milliseconds
    @rtype:             xcb.VoidCookie
    """
    return revent(c, window if not response else root(c),
                  atom(c, 'WM_PROTOCOLS'), [atom(c, '_NET_WM_PING'), timestamp,
                                            window])

def request_wm_ping_checked(c, window, response=False,
                            timestamp=xcb.xproto.Time.CurrentTime):
    """
    Sends an event to root window to ping a window or respond to a ping.

    This protocol allows the Window Manager to determine if the Client is
    still processing X events. This can be used by the Window Manager to
    determine if a window which fails to close after being sent
    WM_DELETE_WINDOW has stopped responding or has stalled for some other
    reason, such as waiting for user confirmation. A Client SHOULD indicate
    that it is willing to participate in this protocol by listing
    _NET_WM_PING in the WM_PROTOCOLS property of the client window.

    A participating Client receiving this message MUST send it back to the
    root window immediately, by setting window = root, and calling
    XSendEvent with the same event mask like all other root window messages
    in this specification use. The Client MUST NOT alter any field in the
    event other than the window. This includes all 5 longs in the data.l[5]
    array. The Window Manager can uniquely identify the ping by the
    timestamp and the data.l[2] field if necessary. Note that some older
    clients may not preserve data.l[2] through data.l[4].

    The Window Manager MAY kill the Client (using _NET_WM_PID) if it fails
    to respond to this protocol within a reasonable time.

    @param c:           An xpyb connection object.
    @param window:      A window identifier.
    @param response:    Whether this is a response to a ping request or not.
    @type timestamp:    Milliseconds
    @rtype:             xcb.VoidCookie
    """
    return revent_checked(c, window if not response else root(c),
                          atom(c, 'WM_PROTOCOLS'), [atom(c, '_NET_WM_PING'),
                                                    timestamp, window])

# _NET_WM_SYNC_REQUEST

def request_wm_sync_request(c, window, req_num,
                            timestamp=xcb.xproto.Time.CurrentTime):
    """
    Sends an event to root window to sync with a client.

    This protocol uses the XSync extension (see the protocol specification
    and the library documentation) to let client and window manager
    synchronize the repaint of the window manager frame and the client
    window. A client indicates that it is willing to participate in the
    protocol by listing _NET_WM_SYNC_REQUEST in the WM_PROTOCOLS property
    of the client window and storing the XID of an XSync counter in the
    property _NET_WM_SYNC_REQUEST_COUNTER. The initial value of this
    counter is not defined by this specification.

    After receiving one or more such message/ConfigureNotify pairs, and
    having handled all repainting associated with the ConfigureNotify
    events, the client MUST set the _NET_WM_SYNC_REQUEST_COUNTER to the 64
    bit number indicated by the data.l[2] and data.l[3] fields of the last
    client message received.

    By using either the Alarm or the Await mechanisms of the XSync
    extension, the window manager can know when the client has finished
    handling the ConfigureNotify events. The window manager SHOULD not
    resize the window faster than the client can keep up.

    The update request number in the client message is determined by the
    window manager subject to the restriction that it MUST NOT be 0. The
    number is generally intended to be incremented by one for each message
    sent. Since the initial value of the XSync counter is not defined by
    this specification, the window manager MAY set the value of the XSync
    counter at any time, and MUST do so when it first manages a new window.

    @param c:           An xpyb connection object.
    @param window:      A window identifier.
    @param req_num:     The XSync request number.
    @type timestamp:    Milliseconds
    @rtype:             xcb.VoidCookie
    """
    high = req_num >> 32
    low = (high << 32) ^ req_num

    return revent(c, window, atom(c, 'WM_PROTOCOLS'),
                  [atom(c, '_NET_WM_SYNC_REQUEST'), timestamp, low, high])

def request_wm_sync_request_checked(c, window, req_num,
                                    timestamp=xcb.xproto.Time.CurrentTime):
    """
    Sends an event to root window to sync with a client.

    This protocol uses the XSync extension (see the protocol specification
    and the library documentation) to let client and window manager
    synchronize the repaint of the window manager frame and the client
    window. A client indicates that it is willing to participate in the
    protocol by listing _NET_WM_SYNC_REQUEST in the WM_PROTOCOLS property
    of the client window and storing the XID of an XSync counter in the
    property _NET_WM_SYNC_REQUEST_COUNTER. The initial value of this
    counter is not defined by this specification.

    After receiving one or more such message/ConfigureNotify pairs, and
    having handled all repainting associated with the ConfigureNotify
    events, the client MUST set the _NET_WM_SYNC_REQUEST_COUNTER to the 64
    bit number indicated by the data.l[2] and data.l[3] fields of the last
    client message received.

    By using either the Alarm or the Await mechanisms of the XSync
    extension, the window manager can know when the client has finished
    handling the ConfigureNotify events. The window manager SHOULD not
    resize the window faster than the client can keep up.

    The update request number in the client message is determined by the
    window manager subject to the restriction that it MUST NOT be 0. The
    number is generally intended to be incremented by one for each message
    sent. Since the initial value of the XSync counter is not defined by
    this specification, the window manager MAY set the value of the XSync
    counter at any time, and MUST do so when it first manages a new window.

    @param c:           An xpyb connection object.
    @param window:      A window identifier.
    @param req_num:     The XSync request number.
    @type timestamp:    Milliseconds
    @rtype:             xcb.VoidCookie
    """
    high = req_num >> 32
    low = (high << 32) ^ req_num

    return revent_checked(c, window, atom(c, 'WM_PROTOCOLS'),
                          [atom(c, '_NET_WM_SYNC_REQUEST'), timestamp, low, high])

# _NET_WM_SYNC_REQUEST_COUNTER

def get_wm_sync_request_counter(c, window):
    """
    Gets XSync counter for this client.

    This protocol uses the XSync extension (see the protocol specification
    and the library documentation) to let client and window manager
    synchronize the repaint of the window manager frame and the client
    window. A client indicates that it is willing to participate in the
    protocol by listing _NET_WM_SYNC_REQUEST in the WM_PROTOCOLS property
    of the client window and storing the XID of an XSync counter in the
    property _NET_WM_SYNC_REQUEST_COUNTER. The initial value of this
    counter is not defined by this specification.

    After receiving one or more such message/ConfigureNotify pairs, and
    having handled all repainting associated with the ConfigureNotify
    events, the client MUST set the _NET_WM_SYNC_REQUEST_COUNTER to the 64
    bit number indicated by the data.l[2] and data.l[3] fields of the last
    client message received.

    By using either the Alarm or the Await mechanisms of the XSync
    extension, the window manager can know when the client has finished
    handling the ConfigureNotify events. The window manager SHOULD not
    resize the window faster than the client can keep up.

    The update request number in the client message is determined by the
    window manager subject to the restriction that it MUST NOT be 0. The
    number is generally intended to be incremented by one for each message
    sent. Since the initial value of the XSync counter is not defined by
    this specification, the window manager MAY set the value of the XSync
    counter at any time, and MUST do so when it first manages a new window.

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @return:        An XSync XID.
    @rtype:         util.PropertyCookieSingle (CARDINAL/32)
    """
    return util.PropertyCookieSingle(
        util.get_property(c, window, atom(c, '_NET_WM_SYNC_REQUEST_COUNTER')))

def get_wm_sync_request_counter_unchecked(c, window):
    """
    Gets XSync counter for this client.

    This protocol uses the XSync extension (see the protocol specification
    and the library documentation) to let client and window manager
    synchronize the repaint of the window manager frame and the client
    window. A client indicates that it is willing to participate in the
    protocol by listing _NET_WM_SYNC_REQUEST in the WM_PROTOCOLS property
    of the client window and storing the XID of an XSync counter in the
    property _NET_WM_SYNC_REQUEST_COUNTER. The initial value of this
    counter is not defined by this specification.

    After receiving one or more such message/ConfigureNotify pairs, and
    having handled all repainting associated with the ConfigureNotify
    events, the client MUST set the _NET_WM_SYNC_REQUEST_COUNTER to the 64
    bit number indicated by the data.l[2] and data.l[3] fields of the last
    client message received.

    By using either the Alarm or the Await mechanisms of the XSync
    extension, the window manager can know when the client has finished
    handling the ConfigureNotify events. The window manager SHOULD not
    resize the window faster than the client can keep up.

    The update request number in the client message is determined by the
    window manager subject to the restriction that it MUST NOT be 0. The
    number is generally intended to be incremented by one for each message
    sent. Since the initial value of the XSync counter is not defined by
    this specification, the window manager MAY set the value of the XSync
    counter at any time, and MUST do so when it first manages a new window.

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @return:        An XSync XID.
    @rtype:         util.PropertyCookieSingle (CARDINAL/32)
    """
    return util.PropertyCookieSingle(
        util.get_property_unchecked(c, window,
                                    atom(c, '_NET_WM_SYNC_REQUEST_COUNTER')))

def set_wm_sync_request_counter(c, window, counter):
    """
    Sets the XSync counter for this client.

    This protocol uses the XSync extension (see the protocol specification
    and the library documentation) to let client and window manager
    synchronize the repaint of the window manager frame and the client
    window. A client indicates that it is willing to participate in the
    protocol by listing _NET_WM_SYNC_REQUEST in the WM_PROTOCOLS property
    of the client window and storing the XID of an XSync counter in the
    property _NET_WM_SYNC_REQUEST_COUNTER. The initial value of this
    counter is not defined by this specification.

    After receiving one or more such message/ConfigureNotify pairs, and
    having handled all repainting associated with the ConfigureNotify
    events, the client MUST set the _NET_WM_SYNC_REQUEST_COUNTER to the 64
    bit number indicated by the data.l[2] and data.l[3] fields of the last
    client message received.

    By using either the Alarm or the Await mechanisms of the XSync
    extension, the window manager can know when the client has finished
    handling the ConfigureNotify events. The window manager SHOULD not
    resize the window faster than the client can keep up.

    The update request number in the client message is determined by the
    window manager subject to the restriction that it MUST NOT be 0. The
    number is generally intended to be incremented by one for each message
    sent. Since the initial value of the XSync counter is not defined by
    this specification, the window manager MAY set the value of the XSync
    counter at any time, and MUST do so when it first manages a new window.

    @param c:           An xpyb connection object.
    @param window:      A window identifier.
    @param counter:     An XSync XID.
    @type counter:      CARDINAL
    @rtype:             xcb.VoidCookie
    """
    packed = struct.pack('I', counter)
    return c.core.ChangeProperty(xcb.xproto.PropMode.Replace, window,
                                 atom(c, '_NET_WM_SYNC_REQUEST_COUNTER'),
                                 CARDINAL, 32, 1,
                                 packed)

def set_wm_sync_request_counter_checked(c, window, counter):
    """
    Sets the XSync counter for this client.

    This protocol uses the XSync extension (see the protocol specification
    and the library documentation) to let client and window manager
    synchronize the repaint of the window manager frame and the client
    window. A client indicates that it is willing to participate in the
    protocol by listing _NET_WM_SYNC_REQUEST in the WM_PROTOCOLS property
    of the client window and storing the XID of an XSync counter in the
    property _NET_WM_SYNC_REQUEST_COUNTER. The initial value of this
    counter is not defined by this specification.

    After receiving one or more such message/ConfigureNotify pairs, and
    having handled all repainting associated with the ConfigureNotify
    events, the client MUST set the _NET_WM_SYNC_REQUEST_COUNTER to the 64
    bit number indicated by the data.l[2] and data.l[3] fields of the last
    client message received.

    By using either the Alarm or the Await mechanisms of the XSync
    extension, the window manager can know when the client has finished
    handling the ConfigureNotify events. The window manager SHOULD not
    resize the window faster than the client can keep up.

    The update request number in the client message is determined by the
    window manager subject to the restriction that it MUST NOT be 0. The
    number is generally intended to be incremented by one for each message
    sent. Since the initial value of the XSync counter is not defined by
    this specification, the window manager MAY set the value of the XSync
    counter at any time, and MUST do so when it first manages a new window.

    @param c:           An xpyb connection object.
    @param window:      A window identifier.
    @param counter:     An XSync XID.
    @type counter:      CARDINAL
    @rtype:             xcb.VoidCookie
    """
    packed = struct.pack('I', counter)
    return c.core.ChangePropertyChecked(xcb.xproto.PropMode.Replace, window,
                                        atom(c,
                                             '_NET_WM_SYNC_REQUEST_COUNTER'),
                                        CARDINAL, 32, 1,
                                        packed)

# _NET_WM_FULLSCREEN_MONITORS

class FullscreenMonitorsCookie(util.PropertyCookie):
    def reply(self):
        v = util.PropertyCookie.reply(self)

        if not v:
            return None

        return {
            'top': v[0],
            'bottom': v[1],
            'left': v[2],
            'right': v[3]
        }

def get_wm_fullscreen_monitors(c, window):
    """
    Get list of monitor edges for this window.

    A read-only list of 4 monitor indices indicating the top, bottom, left,
    and right edges of the window when the fullscreen state is enabled. The
    indices are from the set returned by the Xinerama extension.

    Windows transient for the window with _NET_WM_FULLSCREEN_MONITORS set,
    such as those with type _NEW_WM_WINDOW_TYPE_DIALOG, are generally
    expected to be positioned (e.g. centered) with respect to only one of
    the monitors. This might be the monitor containing the mouse pointer or
    the monitor containing the non-full-screen window.

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @return:        The window's monitor edges.
    @rtype:         FullscreenMonitorsCookie (CARDINAL[4]/32)
    """
    return FullscreenMonitorsCookie(
        util.get_property(c, window, atom(c, '_NET_WM_FULLSCREEN_MONITORS')))

def get_wm_fullscreen_monitors_unchecked(c, window):
    """
    Get list of monitor edges for this window.

    A read-only list of 4 monitor indices indicating the top, bottom, left,
    and right edges of the window when the fullscreen state is enabled. The
    indices are from the set returned by the Xinerama extension.

    Windows transient for the window with _NET_WM_FULLSCREEN_MONITORS set,
    such as those with type _NEW_WM_WINDOW_TYPE_DIALOG, are generally
    expected to be positioned (e.g. centered) with respect to only one of
    the monitors. This might be the monitor containing the mouse pointer or
    the monitor containing the non-full-screen window.

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @return:        The window's monitor edges.
    @rtype:         FullscreenMonitorsCookie (CARDINAL[4]/32)
    """
    return FullscreenMonitorsCookie(
        util.get_property_unchecked(c, window,
                                    atom(c, '_NET_WM_FULLSCREEN_MONITORS')))

def set_wm_fullscreen_monitors(c, window, top, bottom, left, right):
    """
    Sets list of monitor edges for this window.

    A read-only list of 4 monitor indices indicating the top, bottom, left,
    and right edges of the window when the fullscreen state is enabled. The
    indices are from the set returned by the Xinerama extension.

    Windows transient for the window with _NET_WM_FULLSCREEN_MONITORS set,
    such as those with type _NEW_WM_WINDOW_TYPE_DIALOG, are generally
    expected to be positioned (e.g. centered) with respect to only one of
    the monitors. This might be the monitor containing the mouse pointer or
    the monitor containing the non-full-screen window.

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @param top:     The monitor whose top edge defines the top edge of window.
    @param bottom:  The monitor whose bottom edge defines the bottom edge of
                    window.
    @param left:    The monitor whose left edge defines the left edge of
                    window.
    @param right:   The monitor whose right edge defines the right edge of
                    window.
    @rtype:         xcb.VoidCookie
    """
    packed = struct.pack('IIII', top, bottom, left, right)
    return c.core.ChangeProperty(xcb.xproto.PropMode.Replace, window,
                                 atom(c, '_NET_WM_FULLSCREEN_MONITORS'),
                                 CARDINAL, 32, 4,
                                 packed)

def set_wm_fullscreen_monitors_checked(c, window, top, bottom, left, right):
    """
    Sets list of monitor edges for this window.

    A read-only list of 4 monitor indices indicating the top, bottom, left,
    and right edges of the window when the fullscreen state is enabled. The
    indices are from the set returned by the Xinerama extension.

    Windows transient for the window with _NET_WM_FULLSCREEN_MONITORS set,
    such as those with type _NEW_WM_WINDOW_TYPE_DIALOG, are generally
    expected to be positioned (e.g. centered) with respect to only one of
    the monitors. This might be the monitor containing the mouse pointer or
    the monitor containing the non-full-screen window.

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @param top:     The monitor whose top edge defines the top edge of window.
    @param bottom:  The monitor whose bottom edge defines the bottom edge of
                    window.
    @param left:    The monitor whose left edge defines the left edge of
                    window.
    @param right:   The monitor whose right edge defines the right edge of
                    window.
    @rtype:         xcb.VoidCookie
    """
    packed = struct.pack('IIII', top, bottom, left, right)
    return c.core.ChangePropertyChecked(xcb.xproto.PropMode.Replace, window,
                                        atom(c, '_NET_WM_FULLSCREEN_MONITORS'),
                                        CARDINAL, 32, 4,
                                        packed)

def request_wm_fullscreen_monitors(c, window, top, bottom, left, right,
                                   source=1):
    """
    Sends an event to root window to change monitor edges for this window.

    A read-only list of 4 monitor indices indicating the top, bottom, left,
    and right edges of the window when the fullscreen state is enabled. The
    indices are from the set returned by the Xinerama extension.

    Windows transient for the window with _NET_WM_FULLSCREEN_MONITORS set,
    such as those with type _NEW_WM_WINDOW_TYPE_DIALOG, are generally
    expected to be positioned (e.g. centered) with respect to only one of
    the monitors. This might be the monitor containing the mouse pointer or
    the monitor containing the non-full-screen window.

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @param top:     The monitor whose top edge defines the top edge of window.
    @param bottom:  The monitor whose bottom edge defines the bottom edge of
                    window.
    @param left:    The monitor whose left edge defines the left edge of
                    window.
    @param right:   The monitor whose right edge defines the right edge of
                    window.
    @param source:  The source indication.
    @rtype:         xcb.VoidCookie
    """
    return revent(c, window, atom(c, '_NET_WM_FULLSCREEN_MONITORS'),
                  [top, bottom, left, right, source])

def request_wm_fullscreen_monitors_checked(c, window, top, bottom, left, right,
                                           source=1):
    """
    Sends an event to root window to change monitor edges for this window.

    A read-only list of 4 monitor indices indicating the top, bottom, left,
    and right edges of the window when the fullscreen state is enabled. The
    indices are from the set returned by the Xinerama extension.

    Windows transient for the window with _NET_WM_FULLSCREEN_MONITORS set,
    such as those with type _NEW_WM_WINDOW_TYPE_DIALOG, are generally
    expected to be positioned (e.g. centered) with respect to only one of
    the monitors. This might be the monitor containing the mouse pointer or
    the monitor containing the non-full-screen window.

    @param c:       An xpyb connection object.
    @param window:  A window identifier.
    @param top:     The monitor whose top edge defines the top edge of window.
    @param bottom:  The monitor whose bottom edge defines the bottom edge of
                    window.
    @param left:    The monitor whose left edge defines the left edge of
                    window.
    @param right:   The monitor whose right edge defines the right edge of
                    window.
    @param source:  The source indication.
    @rtype:         xcb.VoidCookie
    """
    return revent_checked(c, window, atom(c, '_NET_WM_FULLSCREEN_MONITORS'),
                          [top, bottom, left, right, source])
