"""
Implements the entire EWMH spec. The spec can be found here:
http://standards.freedesktop.org/wm-spec/wm-spec-latest.html

xpybutil's primary purpose was to make accessing ICCCM and EWMH related
information extremely easy. This can be done by using the ewmh or icccm
modules. Here's a quick example (assuming xpybutil is installed):

 ::

  import xpybutil.ewmh as ewmh

  desktop_names = ewmh.get_desktop_names().reply()
  current_desktop = ewmh.get_current_desktop().reply()

  print names.get(current_desktop, current_desktop)

This imports the ewmh module (and by extension, connects to the X server) and
fetches a list of the current desktop names and the current desktop index
(starting from 0). Since not every desktop must be named, the desktop index is
printed if it has no name.

Note that the functions in the ewmh and icccm module return *cookies*. In order
to pull a response from the X server, call the 'reply()' method on a cookie
object. To force a response sent to the X server, call the 'check()' method on
the corresponding cookie.

Much of the EWMH and ICCCM modules encapsulate packing data from convenient
Python data types into C structs (using the 'struct' Python module). For
example, if one wants to fetch the partial struts set by some window with
identifier ID, you could do:

 ::

  import xpybutil.ewmh as ewmh

  print ewmh.get_wm_strut_partial(ID).reply()

Which outputs a dictionary with 12 entries, where each corresponds to a value
in the partial strut. (i.e., 'left', 'top_end_x', 'right_start_y', etc...).

In general, particularly with the EWMH module, the ewmh module is very nearly
representative of the spec itself. Functions that get property values start
with ``get_``, functions that set property values start with ``set_``, and
functions that send an event to a client (which typically requests the window
manager to DO something) start with ``request_``.

If a request has no reply (typically the ``set_`` functions), then the
default is to call it 'unchecked'. If you want to check the result (and force
retrieval), then use the '_checked' variant.

The reverse goes for the ``get_`` functions. By default, they are checked, but
you can use the '_unchecked' variant too.

Basically, you should probably almost always use the 'checked' variant of
everything. The cases where you don't are when you want to send a whole bunch
of requests to the X server at once. You could use the unchecked invariant, and
after you've initialized all the cookies, calling 'flush' will force
communication with the X server.

Finally, unless you're writing a window manager or creating a client window
from scratch, you'll almost always want to use the ``get_`` and ``request_``
functions, not ``set_``. For example, if you want to change the current
desktop...

  DON'T DO: ``ewmh.set_current_desktop_checked(2).check()``

  DO:       ``ewmh.request_current_desktop_checked(2).check()``

The former will probably not work, but the latter will. Just follow the EWMH
spec :-)
"""
import struct

from xpybutil.compat import xproto

from xpybutil import conn as c, root, event, util

__atoms = [
   # Non-standard
   '_NET_VISIBLE_DESKTOPS', '_NET_WM_WINDOW_OPACITY',

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
revent = event.root_send_client_event
revent_checked = event.root_send_client_event_checked
ATOM = xproto.Atom.ATOM
CARDINAL = xproto.Atom.CARDINAL
WINDOW = xproto.Atom.WINDOW

# Build the atom cache for quicker access
util.build_atom_cache(__atoms)


# _NET_SUPPORTED

def get_supported():
    """
    Returns a list of hints supported by the window manager.

    :return:        A list of atoms in the _NET_SUPPORTED property.
    :rtype:         util.PropertyCookie (ATOM[]/32)
    """
    return util.PropertyCookie(util.get_property(root, '_NET_SUPPORTED'))

def get_supported_unchecked():
    return util.PropertyCookie(util.get_property_unchecked(root,
                                                           '_NET_SUPPORTED'))

def set_supported(atoms):
    """
    Sets the list of hints supported by the window manager.

    :param atoms:   A list of atom identifiers.
    :type atoms:    ATOM[]/32
    :rtype:         xcb.VoidCookie
    """
    packed = struct.pack('I' * len(atoms), *atoms)
    return c.core.ChangeProperty(xproto.PropMode.Replace, root,
                                 atom('_NET_SUPPORTED'), ATOM, 32, len(atoms),
                                 packed)

def set_supported_checked(atoms):
    packed = struct.pack('I' * len(atoms), *atoms)
    return c.core.ChangePropertyChecked(xproto.PropMode.Replace, root,
                                        atom('_NET_SUPPORTED'),
                                        ATOM, 32, len(atoms), packed)

# _NET_CLIENT_LIST

def get_client_list():
    """
    Returns a list of windows managed by the window manager.

    :return:        A list of window identifiers.
    :rtype:         util.PropertyCookie (ATOM[]/32)
    """
    return util.PropertyCookie(util.get_property(root, '_NET_CLIENT_LIST'))

def get_client_list_unchecked():
    return util.PropertyCookie(util.get_property_unchecked(root,
                                                           '_NET_CLIENT_LIST'))

def set_client_list(windows):
    """
    Sets the list of windows managed by the window manager.

    :param windows: A list of atom identifiers.
    :type windows:  ATOM[]/32
    :rtype:         xcb.VoidCookie
    """
    packed = struct.pack('I' * len(windows), *windows)
    return c.core.ChangeProperty(xproto.PropMode.Replace, root,
                                 atom('_NET_CLIENT_LIST'),
                                 WINDOW, 32, len(windows), packed)

def set_client_list_checked(windows):
    packed = struct.pack('I' * len(windows), *windows)
    return c.core.ChangePropertyChecked(xproto.PropMode.Replace, root,
                                        atom('_NET_CLIENT_LIST'),
                                        WINDOW, 32, len(windows), packed)

# _NET_CLIENT_LIST_STACKING

def get_client_list_stacking():
    """
    Returns the window stacking order.

    :return:        A list of window identifiers.
    :rtype:         util.PropertyCookie (ATOM[]/32)
    """
    return util.PropertyCookie(util.get_property(root,
                                                 '_NET_CLIENT_LIST_STACKING'))

def get_client_list_stacking_unchecked():
    cook = util.get_property_unchecked(root, '_NET_CLIENT_LIST_STACKING')
    return util.PropertyCookie(cook)

def set_client_list_stacking(windows):
    """
    Sets the window stacking order.

    :param windows: A list of atom identifiers.
    :type windows:  ATOM[]/32
    :rtype:         xcb.VoidCookie
    """
    packed = struct.pack('I' * len(windows), *windows)
    return c.core.ChangeProperty(xproto.PropMode.Replace, root,
                                 atom('_NET_CLIENT_LIST_STACKING'),
                                 WINDOW, 32, len(windows), packed)

def set_client_list_stacking_checked(windows):
    packed = struct.pack('I' * len(windows), *windows)
    return c.core.ChangePropertyChecked(xproto.PropMode.Replace, root,
                                 atom('_NET_CLIENT_LIST_STACKING'),
                                 WINDOW, 32, len(windows), packed)

# _NET_NUMBER_DESKTOPS

def get_number_of_desktops():
    """
    Returns the number of virtual desktops.

    :return:        The number of desktops.
    :rtype:         util.PropertyCookieSingle (CARDINAL/32)
    """
    cook = util.get_property(root, '_NET_NUMBER_OF_DESKTOPS')
    return util.PropertyCookieSingle(cook)

def get_number_of_desktops_unchecked():
    cook = util.get_property_unchecked(root, '_NET_NUMBER_OF_DESKTOPS')
    return util.PropertyCookieSingle(cook)

def set_number_of_desktops(number_of_desktops):
    """
    Sets the number of desktops.

    :param number_of_desktops:  The number of desktops.
    :type number_of_desktops:   CARDINAL/32
    :rtype:                     xcb.VoidCookie
    """
    packed = struct.pack('I', number_of_desktops)
    return c.core.ChangeProperty(xproto.PropMode.Replace, root,
                                 atom('_NET_NUMBER_OF_DESKTOPS'), CARDINAL, 32,
                                 1, packed)

def set_number_of_desktops_checked(number_of_desktops):
    packed = struct.pack('I', number_of_desktops)
    return c.core.ChangePropertyChecked(xproto.PropMode.Replace, root,
                                        atom('_NET_NUMBER_OF_DESKTOPS'),
                                        CARDINAL, 32, 1, packed)

def request_number_of_desktops(number_of_desktops):
    """
    Sends event to root window to set the number of desktops.

    :param number_of_desktops:  The number of desktops.
    :type number_of_desktops:   CARDINAL/32
    :rtype:                     xcb.VoidCookie
    """
    return revent(root, '_NET_NUMBER_OF_DESKTOPS', number_of_desktops)

def request_number_of_desktops_checked(number_of_desktops):
    return revent_checked(root, '_NET_NUMBER_OF_DESKTOPS', number_of_desktops)

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

def get_desktop_geometry():
    """Returns the desktop geometry.

    :return:        A desktop geometry dictionary.
                    Keys: width, height
    :rtype:         DesktopGeometryCookie (CARDINAL[2]/32)
    """
    return DesktopGeometryCookie(util.get_property(root,
                                                   '_NET_DESKTOP_GEOMETRY'))

def get_desktop_geometry_unchecked():
    cook = util.get_property_unchecked(root, '_NET_DESKTOP_GEOMETRY')
    return DesktopGeometryCookie(cook)

def set_desktop_geometry(width, height):
    """
    Sets the desktop geometry.

    :param width:               The width of the desktop.
    :type width:                CARDINAL/32
    :param height:              The height of the desktop.
    :type height:               CARDINAL/32
    :rtype:                     xcb.VoidCookie
    """
    packed = struct.pack('II', width, height)
    return c.core.ChangeProperty(xproto.PropMode.Replace, root,
                                 atom('_NET_DESKTOP_GEOMETRY'), CARDINAL, 32, 2,
                                 packed)

def set_desktop_geometry_checked(width, height):
    packed = struct.pack('II', width, height)
    return c.core.ChangePropertyChecked(xproto.PropMode.Replace, root,
                                        atom('_NET_DESKTOP_GEOMETRY'),
                                        CARDINAL, 32, 2, packed)

def request_desktop_geometry(width, height):
    """
    Sends event to root window to set the desktop geometry.

    :param width:               The width of the desktop.
    :type width:                CARDINAL/32
    :param height:              The height of the desktop.
    :type height:               CARDINAL/32
    :rtype:                     xcb.VoidCookie
    """
    return revent(root, '_NET_DESKTOP_GEOMETRY', width, height)

def request_desktop_geometry_checked(width, height):
    return revent_checked(root, '_NET_DESKTOP_GEOMETRY', width, height)

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

def get_desktop_viewport():
    """
    Returns x,y pairs defining the top-left corner of each desktop's viewport.

    :return:        A list of desktop viewport dictionaries.

                    Keys: x, y
    :rtype:         DesktopViewportCookie (CARDINAL[][2]/32)
    """
    return DesktopViewportCookie(util.get_property(root,
                                                   '_NET_DESKTOP_VIEWPORT'))

def get_desktop_viewport_unchecked():
    cook = util.get_property_unchecked(root, '_NET_DESKTOP_VIEWPORT')
    return DesktopViewportCookie(cook)

def set_desktop_viewport(pairs):
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

    :param pairs:               A list of x,y dictionary pairs.
    :type pairs:                CARDINAL[][2]/32
    :rtype:                     xcb.VoidCookie
    """
    flatten = []
    for pair in pairs:
        flatten.append(pair['x'])
        flatten.append(pair['y'])

    packed = struct.pack('I' * len(flatten), *flatten)
    return c.core.ChangeProperty(xproto.PropMode.Replace, root,
                                 atom('_NET_DESKTOP_VIEWPORT'),
                                 CARDINAL, 32, len(flatten), packed)

def set_desktop_viewport_checked(pairs):
    flatten = []
    for pair in pairs:
        flatten.append(pair['x'])
        flatten.append(pair['y'])

    packed = struct.pack('I' * len(flatten), *flatten)
    return c.core.ChangePropertyChecked(xproto.PropMode.Replace, root,
                                        atom('_NET_DESKTOP_VIEWPORT'),
                                        CARDINAL, 32, len(flatten), packed)

def request_desktop_viewport(x, y):
    """
    Sends event to root window to set the viewport position of current desktop.

    :param x:       The x position of the top-left corner.
    :type x:        CARDINAL/32
    :param y:       The y position of the top-left corner.
    :type y:        CARDINAL/32
    :rtype:         xcb.VoidCookie
    """
    return revent(root, '_NET_DESKTOP_VIEWPORT', x, y)

def request_desktop_viewport_checked(x, y):
    return revent_checked(root, '_NET_DESKTOP_VIEWPORT', x, y)

# _NET_CURRENT_DESKTOP

def get_current_desktop():
    """
    Returns the current desktop number.

    :return:        The index of the current desktop.
    :rtype:         util.PropertyCookieSingle (CARDINAL/32)
    """
    return util.PropertyCookieSingle(util.get_property(root,
                                                       '_NET_CURRENT_DESKTOP'))

def get_current_desktop_unchecked():
    cook = util.get_property_unchecked(root, '_NET_CURRENT_DESKTOP')
    return util.PropertyCookieSingle(cook)

def set_current_desktop(current_desktop):
    """
    Sets the current desktop number.

    :param current_desktop:     The current desktop index.
    :type current_desktop:      CARDINAL/32
    :rtype:                     xcb.VoidCookie
    """
    packed = struct.pack('I', current_desktop)
    return c.core.ChangeProperty(xproto.PropMode.Replace, root,
                                 atom('_NET_CURRENT_DESKTOP'), CARDINAL, 32, 1,
                                 packed)

def set_current_desktop_checked(current_desktop):
    packed = struct.pack('I', current_desktop)
    return c.core.ChangePropertyChecked(xproto.PropMode.Replace, root,
                                        atom('_NET_CURRENT_DESKTOP'),
                                        CARDINAL, 32, 1, packed)

def request_current_desktop(desktop_number,
                            timestamp=xproto.Time.CurrentTime):
    """
    Sends event to root window to set the current desktop.

    :param desktop_number:      The current desktop index.
    :type desktop_number:       CARDINAL/32
    :type timestamp:            Milliseconds.
    :rtype:                     xcb.VoidCookie
    """
    return revent(root, '_NET_CURRENT_DESKTOP', desktop_number, timestamp)

def request_current_desktop_checked(desktop_number,
                                    timestamp=xproto.Time.CurrentTime):
    return revent_checked(root, '_NET_CURRENT_DESKTOP',
                          desktop_number, timestamp)

# _NET_VISIBLE_DESKTOPS

def get_visible_desktops():
    """
    Returns a list of visible desktops.

    The first desktop is on Xinerama screen 0, the second is on Xinerama
    screen 1, etc.

    :return:        A list of visible desktops.
    :rtype:         util.PropertyCookie (CARDINAL[]/32)
    """
    return util.PropertyCookie(util.get_property(root, '_NET_VISIBLE_DESKTOPS'))

def get_visible_desktops_unchecked():
    cook = util.get_property_unchecked(root, '_NET_VISIBLE_DESKTOPS')
    return util.PropertyCookie(cook)

def set_visible_desktops(desktops):
    """
    Sets the list of visible desktops.

    :param desktops: A list of desktops.
    :type desktops:  CARDINAL[]/32
    :rtype:          xcb.VoidCookie
    """
    packed = struct.pack('I' * len(desktops), *desktops)
    return c.core.ChangeProperty(xproto.PropMode.Replace, root,
                                 atom('_NET_VISIBLE_DESKTOPS'),
                                 CARDINAL, 32, len(desktops), packed)

def set_visible_desktops_checked(desktops):
    packed = struct.pack('I' * len(desktops), *desktops)
    return c.core.ChangePropertyChecked(xproto.PropMode.Replace, root,
                                        atom('_NET_VISIBLE_DESKTOPS'),
                                        CARDINAL, 32, len(desktops), packed)

# _NET_DESKTOP_NAMES

def get_desktop_names():
    """
    Returns a list of names of the virtual desktops.

    :return:        A list of virutal desktop names.
    :rtype:         util.PropertyCookie (UTF8_STRING[])
    """
    return util.PropertyCookie(util.get_property(root, '_NET_DESKTOP_NAMES'))

def get_desktop_names_unchecked():
    cook = util.get_property_unchecked(root, '_NET_DESKTOP_NAMES')
    return util.PropertyCookie(cook)

def set_desktop_names(desktop_names):
    """
    Sets the current list of desktop names.

    :param desktop_names:   A list of new desktop names.
    :type desktop_names:    UTF8_STRING[]
    :rtype:                 xcb.VoidCookie
    """
    # Null terminate the list of desktop names
    nullterm = []
    for desktop_name in desktop_names:
        nullterm.append(desktop_name + chr(0))
    nullterm = ''.join(nullterm)

    return c.core.ChangeProperty(xproto.PropMode.Replace, root,
                                 atom('_NET_DESKTOP_NAMES'),
                                 atom('UTF8_STRING'), 8,
                                 len(nullterm), nullterm)

def set_desktop_names_checked(desktop_names):
    # Null terminate the list of desktop names
    nullterm = []
    for desktop_name in desktop_names:
        nullterm.append(desktop_name + chr(0))
    nullterm = ''.join(nullterm)

    return c.core.ChangePropertyChecked(xproto.PropMode.Replace, root,
                                        atom('_NET_DESKTOP_NAMES'),
                                        atom('UTF8_STRING'), 8,
                                        len(nullterm), nullterm)

# _NET_ACTIVE_WINDOW

def get_active_window():
    """
    Returns the identifier of the currently active window.

    :return:        The window ID of the active window.
    :rtype:         util.PropertyCookieSingle (WINDOW/32)
    """
    return util.PropertyCookieSingle(util.get_property(root,
                                                       '_NET_ACTIVE_WINDOW'))

def get_active_window_unchecked():
    cook = util.get_property_unchecked(root, '_NET_ACTIVE_WINDOW')
    return util.PropertyCookieSingle(cook)

def set_active_window(active):
    """
    Sets the identifier of the currently active window.

    :param active:  The identifier of the window that is active.
    :type active:   WINDOW/32
    :rtype:         xcb.VoidCookie
    """
    packed = struct.pack('I', active)
    return c.core.ChangeProperty(xproto.PropMode.Replace, root,
                                 atom('_NET_ACTIVE_WINDOW'),
                                 WINDOW, 32, 1, packed)

def set_active_window_checked(active):
    packed = struct.pack('I', active)
    return c.core.ChangePropertyChecked(xproto.PropMode.Replace, root,
                                        atom('_NET_ACTIVE_WINDOW'),
                                        WINDOW, 32, 1, packed)

def request_active_window(active, source=1,
                          timestamp=xproto.Time.CurrentTime,
                          current=0):
    """
    Sends event to root window to set the active window.

    :param active:      The window ID of the window to make active.
    :type active:       WINDOW/32
    :param source:      The source indication.
    :type timestamp:    Milliseconds
    :param current:     Client's active toplevel window
    :rtype:             xcb.VoidCookie
    """
    return revent(active, '_NET_ACTIVE_WINDOW', source, timestamp, current)

def request_active_window_checked(active, source=1,
                                  timestamp=xproto.Time.CurrentTime,
                                  current=0):
    return revent_checked(active, '_NET_ACTIVE_WINDOW', source, timestamp,
                          current)

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

def get_workarea():
    """
    Returns the x, y, width and height defining the desktop workarea.

    :return:        A list of workarea dictionaries.

                    Keys: x, y, width, height
    :rtype:         util.WorkareaCookie (CARDINAL[][4]/32)
    """
    return WorkareaCookie(util.get_property(root, '_NET_WORKAREA'))

def get_workarea_unchecked():
    return WorkareaCookie(util.get_property_unchecked(root, '_NET_WORKAREA'))

def set_workarea(workareas):
    """
    Sets the workarea (x, y, width, height) for each desktop.

    :param workareas:   A list of x,y,width,height dictionaries.
    :type workareas:    CARDINAL[][4]/32
    :rtype:             xcb.VoidCookie
    """
    flatten = []
    for workarea in workareas:
        flatten.append(workarea['x'])
        flatten.append(workarea['y'])
        flatten.append(workarea['width'])
        flatten.append(workarea['height'])
    packed = struct.pack('I' * len(flatten), *flatten)

    return c.core.ChangeProperty(xproto.PropMode.Replace, root,
                                 atom('_NET_WORKAREA'), CARDINAL, 32,
                                 len(flatten), packed)

def set_workarea_checked(workareas):
    flatten = []
    for workarea in workareas:
        flatten.append(workarea['x'])
        flatten.append(workarea['y'])
        flatten.append(workarea['width'])
        flatten.append(workarea['height'])
    packed = struct.pack('I' * len(flatten), *flatten)

    return c.core.ChangePropertyChecked(xproto.PropMode.Replace, root,
                                        atom('_NET_WORKAREA'), CARDINAL, 32,
                                        len(flatten), packed)

# _NET_SUPPORTING_WM_CHECK

def get_supporting_wm_check(wid):
    """
    Returns the identifier of the child window created by the window manager.

    :param wid:     The identifier of the window with the property.
    :type wid:      WINDOW/32
    :return:        The window ID of the child window.
    :rtype:         util.PropertyCookieSingle (WINDOW/32)
    """
    cook = util.get_property(wid, '_NET_SUPPORTING_WM_CHECK')
    return util.PropertyCookieSingle(cook)

def get_supporting_wm_check_unchecked(wid):
    cook = util.get_property_unchecked(wid, '_NET_SUPPORTING_WM_CHECK')
    return util.PropertyCookieSingle(cook)

def set_supporting_wm_check(wid, child):
    """
    Sets the identifier of the child window created by the window manager.

    :param wid:     The identifier of the window with the property.
    :type wid:      WINDOW/32
    :param child:   The identifier of the child window.
    :type child:    WINDOW/32
    :rtype:         xcb.VoidCookie
    """
    packed = struct.pack('I', child)
    return c.core.ChangeProperty(xproto.PropMode.Replace, wid,
                                 atom('_NET_SUPPORTING_WM_CHECK'),
                                 WINDOW, 32, 1, packed)

def set_supporting_wm_check_checked(wid, child):
    packed = struct.pack('I', child)
    return c.core.ChangePropertyChecked(xproto.PropMode.Replace, wid,
                                        atom('_NET_SUPPORTING_WM_CHECK'),
                                        WINDOW, 32, 1, packed)

# _NET_VIRTUAL_ROOTS

def get_virtual_roots():
    """
    Returns a list of identifiers for the virtual root windows.

    :return:        A list of window identifiers for the virtual root windows.
    :rtype:         util.PropertyCookie (WINDOW[]/32)
    """
    return util.PropertyCookie(util.get_property(root, '_NET_VIRTUAL_ROOTS'))

def get_virtual_roots_unchecked():
    cook = util.get_property_unchecked(root, '_NET_VIRTUAL_ROOTS')
    return util.PropertyCookie(cook)

def set_virtual_roots(vroots):
    """
    Sets the identifiers of the virtual root windows.

    :param vroots:  A list of window identifiers for the virtual root windows.
    :type vroots:   WINDOW[]/32
    :rtype:         xcb.VoidCookie
    """
    packed = struct.pack('I' * len(vroots), *vroots)
    return c.core.ChangeProperty(xproto.PropMode.Replace, root,
                                 atom('_NET_VIRTUAL_ROOTS'),
                                 WINDOW, 32, len(vroots), packed)

def set_virtual_roots_checked(vroots):
    packed = struct.pack('I' * len(vroots), *vroots)
    return c.core.ChangePropertyChecked(xproto.PropMode.Replace, root,
                                        atom('_NET_VIRTUAL_ROOTS'),
                                        WINDOW, 32, len(vroots), packed)

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

def get_desktop_layout():
    """
    Returns the desktop layout.

    :return:        A desktop layout dictionary.

                    Keys: orientation, columns, rows, starting_corner
    :rtype:         DesktopLayoutCookie (CARDINAL[4]/32)
    """
    return DesktopLayoutCookie(util.get_property(root, '_NET_DESKTOP_LAYOUT'))

def get_desktop_layout_unchecked():
    cook = util.get_property_unchecked(root, '_NET_DESKTOP_LAYOUT')
    return DesktopLayoutCookie(cook)

def set_desktop_layout(orientation, columns, rows,
                       starting_corner=StartingCorner.TopLeft):
    """
    Sets the desktop layout.

    :param orientation:         Horizontal or vertical orientation.
    :type orientation:          CARDINAL/32
    :param columns:             Number of columns.
    :type columns:              CARDINAL/32
    :param rows:                Number of rows.
    :type rows:                 CARDINAL/32
    :param starting_corner:     Top left, top right, bottom right, or bottom
                                left may be specified as a starting corner.
    :type starting_corner:      CARDINAL/32
    :rtype:                     xcb.VoidCookie
    """
    packed = struct.pack('IIII', orientation, columns, rows, starting_corner)
    return c.core.ChangeProperty(xproto.PropMode.Replace, root,
                                 atom('_NET_DESKTOP_LAYOUT'),
                                 CARDINAL, 32, 4, packed)

def set_desktop_layout_checked(orientation, columns, rows,
                               starting_corner=StartingCorner.TopLeft):
    packed = struct.pack('IIII', orientation, columns, rows, starting_corner)
    return c.core.ChangePropertyChecked(xproto.PropMode.Replace, root,
                                        atom('_NET_DESKTOP_LAYOUT'),
                                        CARDINAL, 32, 4, packed)

# _NET_SHOWING_DESKTOP

class ShowingDesktopCookie(util.PropertyCookieSingle):
    def reply(self):
        v = util.PropertyCookieSingle.reply(self)

        if v is None:
            return None

        if v == 1:
            return True
        return False

def get_showing_desktop():
    """
    Returns whether the window manager is in "showing the desktop" mode.

    :return:        Boolean whether the window manager is in "showing desktop"
                    mode or not.
    :rtype:         ShowingDesktopCookie (CARDINAL/32)
    """
    return ShowingDesktopCookie(util.get_property(root, '_NET_SHOWING_DESKTOP'))

def get_showing_desktop_unchecked():
    cook = util.get_property_unchecked(root, '_NET_SHOWING_DESKTOP')
    return ShowingDesktopCookie(cook)

def set_showing_desktop(showing_desktop):
    """
    Sets whether the window is in "showing the desktop" mode.

    :param showing_desktop:  Boolean whether the window manager is in "showing
                             desktop" mode or not.
    :type showing_desktop:   CARDINAL/32
    :rtype:                  xcb.VoidCookie
    """
    return c.core.ChangeProperty(xproto.PropMode.Replace, root,
                                 atom('_NET_SHOWING_DESKTOP'), CARDINAL, 32, 1,
                                 [showing_desktop])

def set_showing_desktop_checked(showing_desktop):
    return c.core.ChangePropertyChecked(xproto.PropMode.Replace, root,
                                        atom('_NET_SHOWING_DESKTOP'),
                                        CARDINAL, 32, 1, [showing_desktop])

def request_showing_desktop(showing_desktop):
    """
    Sends event to root window to put window manager in "showing desktop" mode.

    :param showing_desktop:  Boolean whether the window manager is in "showing
                             desktop" mode or not.
    :type showing_desktop:   CARDINAL/32
    :rtype:                  xcb.VoidCookie
    """
    return revent(root, '_NET_SHOWING_DESKTOP', showing_desktop)

def request_showing_desktop_checked(showing_desktop):
    return revent_checked(root, '_NET_SHOWING_DESKTOP', showing_desktop)

# _NET_CLOSE_WINDOW

def request_close_window(window, timestamp=xproto.Time.CurrentTime,
                         source=1):
    """
    Sends event to root window to close a window.

    :param window:      A window identifier.
    :param source:      The source indication.
    :type timestamp:    Milliseconds
    :rtype:             xcb.VoidCookie
    """
    return revent(window, '_NET_CLOSE_WINDOW', timestamp, source)

def request_close_window_checked(window, timestamp=xproto.Time.CurrentTime,
                                 source=1):
    return revent_checked(window, '_NET_CLOSE_WINDOW', timestamp, source)

# _NET_MOVERESIZE_WINDOW

def request_moveresize_window(window, x=None, y=None, width=None,
                              height=None,
                              gravity=xproto.Gravity.BitForget, source=1):
    """
    Sends event to root window to move/resize a window.

    :param window:      A window identifier.
    :param x:           x coordinate
    :param y:           y coordinate
    :param width:       Width
    :param height:      Height
    :param gravity:     Should be one of NorthWest, North, NorthEast, West,
                        Center, East, SouthWest, South, SouthEast, and Static.
                        If set to 0, the window manager should use the default
                        gravity for the window.
    :param source:      The source indication.
    :rtype:             xcb.VoidCookie
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

    return revent(window, '_NET_MOVERESIZE_WINDOW',
                  flags, x or 0, y or 0, width or 0, height or 0)

def request_moveresize_window_checked(window, x=None, y=None, width=None,
                                      height=None,
                                      gravity=xproto.Gravity.BitForget,
                                      source=1):
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

    return revent_checked(window, '_NET_MOVERESIZE_WINDOW',
                          flags, x, y, width, height)

# _NET_WM_MOVERESIZE

def request_wm_moveresize(window, direction, x_root=0, y_root=0,
                          button=0, source=1):
    """
    Sends event to root window to initiate window movement or resizing.

    :param window:      A window identifier.
    :param direction:   Whether it is moving or resizing, and if resizing,
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
    :param x_root:      x coordinate of the pointer.
    :param y_root:      y coordinate of the pointer.
    :param button:      Which button was pressed, if a mouse button was used
                        to initiate this request.
    :param source:      The source indication.
    :rtype:             xcb.VoidCookie
    """
    return revent(window, '_NET_WM_MOVERESIZE',
                  x_root, y_root, direction, button, source)

def request_wm_moveresize_checked(window, direction, x_root=0, y_root=0,
                                  button=0, source=1):
    return revent_checked(window, '_NET_WM_MOVERESIZE',
                          x_root, y_root, direction, button, source)

# _NET_RESTACK_WINDOW

def request_restack_window(window, stack_mode=xproto.StackMode.Above,
                           sibling=0, source=1):
    """
    Sends event to root window to restack a window.

    :param window:      A window identifier.
    :param stack_mode:  Stacking mode of window. Can be one of the following
                        flags: Above, Below, TopIf, BottomIf, Opposite
    :param sibling:     A sibling window identifier.
    :param source:      The source indication.
    :rtype:             xcb.VoidCookie
    """
    return revent(window, '_NET_RESTACK_WINDOW', source, sibling, stack_mode)

def request_restack_window_checked(window,
                                   stack_mode=xproto.StackMode.Above,
                                   sibling=0, source=2):
    return revent_checked(window, '_NET_RESTACK_WINDOW',
                          source, sibling, stack_mode)

# _NET_REQUEST_FRAME_EXTENTS

def request_request_frame_extents(window):
    """
    Sends event to root window ask the WM to estimate the frame extents.

    :param window:      A window identifier.
    :rtype:             xcb.VoidCookie
    """
    return revent(window, '_NET_REQUEST_FRAME_EXTENTS')

def request_request_frame_extents_checked(window):
    return revent_checked(window, '_NET_REQUEST_FRAME_EXTENTS')

# _NET_WM_NAME

def get_wm_name(window):
    """
    Get the title of a window.

    :param window:  A window identifier.
    :return:        The window's title.
    :rtype:         util.PropertyCookie (UTF8_STRING)
    """
    return util.PropertyCookie(util.get_property(window, '_NET_WM_NAME'))

def get_wm_name_unchecked(window):
    return util.PropertyCookie(util.get_property_unchecked(window,
                                                           '_NET_WM_NAME'))

def set_wm_name(window, wm_name):
    """
    Sets the title of a window.

    :param window:  A window identifier.
    :param wm_name: The title of the window.
    :rtype:         xcb.VoidCookie
    """
    return c.core.ChangeProperty(xproto.PropMode.Replace, window,
                                 atom('_NET_WM_NAME'),
                                 atom('UTF8_STRING'), 8, len(wm_name), wm_name)

def set_wm_name_checked(window, wm_name):
    return c.core.ChangePropertyChecked(xproto.PropMode.Replace, window,
                                        atom('_NET_WM_NAME'),
                                        atom('UTF8_STRING'), 8, len(wm_name),
                                        wm_name)

# _NET_WM_VISIBLE_NAME

def get_wm_visible_name(window):
    """
    Get the visible title of a window.

    :param window:  A window identifier.
    :return:        The window's visible title.
    :rtype:         util.PropertyCookie (UTF8_STRING)
    """
    return util.PropertyCookie(util.get_property(window,
                                                 '_NET_WM_VISIBLE_NAME'))

def get_wm_visible_name_unchecked(window):
    cook = util.get_property_unchecked(window, '_NET_WM_VISIBLE_NAME')
    return util.PropertyCookie(cook)

def set_wm_visible_name(window, wm_name):
    """
    Sets the visible title of a window.

    :param window:  A window identifier.
    :param wm_name: The title of the window.
    :rtype:         xcb.VoidCookie
    """
    return c.core.ChangeProperty(xproto.PropMode.Replace, window,
                                 atom('_NET_WM_VISIBLE_NAME'),
                                 atom('UTF8_STRING'), 8, len(wm_name), wm_name)

def set_wm_visible_name_checked(window, wm_name):
    return c.core.ChangePropertyChecked(xproto.PropMode.Replace, window,
                                        atom('_NET_WM_VISIBLE_NAME'),
                                        atom('UTF8_STRING'), 8, len(wm_name),
                                        wm_name)

# _NET_WM_ICON_NAME

def get_wm_icon_name(window):
    """
    Get the icon name of a window.

    :param window:  A window identifier.
    :return:        The window's icon name.
    :rtype:         util.PropertyCookie (UTF8_STRING)
    """
    return util.PropertyCookie(util.get_property(window, '_NET_WM_ICON_NAME'))

def get_wm_icon_name_unchecked(window):
    cook = util.get_property_unchecked(window, '_NET_WM_ICON_NAME')
    return util.PropertyCookie(cook)

def set_wm_icon_name(window, icon_name):
    """
    Sets the icon name of a window.

    :param window:      A window identifier.
    :param icon_name:   The icon name of the window.
    :rtype:             xcb.VoidCookie
    """
    return c.core.ChangeProperty(xproto.PropMode.Replace, window,
                                 atom('_NET_WM_ICON_NAME'), atom('UTF8_STRING'),
                                 8, len(icon_name), icon_name)

def set_wm_icon_name_checked(window, icon_name):
    return c.core.ChangePropertyChecked(xproto.PropMode.Replace, window,
                                        atom('_NET_WM_ICON_NAME'),
                                        atom('UTF8_STRING'), 8, len(icon_name),
                                        icon_name)

# _NET_WM_VISIBLE_ICON_NAME

def get_wm_visible_icon_name(window):
    """
    Get the visible icon name of a window.

    :param window:  A window identifier.
    :return:        The window's visible icon name.
    :rtype:         util.PropertyCookie (UTF8_STRING)
    """
    return util.PropertyCookie(util.get_property(window,
                                                 '_NET_WM_VISIBLE_ICON_NAME'))

def get_wm_visible_icon_name_unchecked(window):
    cook = util.get_property_unchecked(window, '_NET_WM_VISIBLE_ICON_NAME')
    return util.PropertyCookie(cook)

def set_wm_visible_icon_name(window, icon_name):
    """
    Sets the visible icon name of a window.

    :param window:      A window identifier.
    :param icon_name:   The icon name of the window.
    :rtype:             xcb.VoidCookie
    """
    return c.core.ChangeProperty(xproto.PropMode.Replace, window,
                                 atom('_NET_WM_VISIBLE_ICON_NAME'),
                                 atom('UTF8_STRING'), 8, len(icon_name),
                                 icon_name)

def set_wm_visible_icon_name_checked(window, icon_name):
    return c.core.ChangePropertyChecked(xproto.PropMode.Replace, window,
                                        atom('_NET_WM_VISIBLE_ICON_NAME'),
                                        atom('UTF8_STRING'), 8, len(icon_name),
                                        icon_name)

# _NET_WM_WINDOW_OPACITY

class OpacityCookieSingle(util.PropertyCookieSingle):
    def reply(self):
        v = util.PropertyCookieSingle.reply(self)

        if not v:
            return None

        return float(v) / float(0xffffffff)

def get_wm_window_opacity(window):
    """
    Get the opacity of the current window.

    N.B. If your window manager uses decorations, you'll typically want to pass
    your client's *parent* window to this function.

    :param window:  A window identifier.
    :return:        An opacity percentage between 0 and 1 (inclusive)
    :rtype:         util.PropertyCookieSingle (CARDINAL/32)
    """
    return OpacityCookieSingle(util.get_property(window,
                                                 '_NET_WM_WINDOW_OPACITY'))

def get_wm_window_opacity_unchecked(window):
    cook = util.get_property_unchecked(window, '_NET_WM_WINDOW_OPACITY')
    return OpacityCookieSingle(cook)

def set_wm_window_opacity(window, opacity):
    """
    Sets the opacity of the current window.

    N.B. If your window manager uses decorations, you'll typically want to pass
    your client's *parent* window to this function.

    :param window:  A window identifier.
    :param opacity: A float between 0 and 1 inclusive.

                    0 is completely transparent and 1 is completely opaque.
    :type opacity:  CARDINAL/32
    :rtype:         xcb.VoidCookie
    """
    assert 0 <= opacity <= 1
    packed = struct.pack('I', int(opacity * 0xffffffff))
    return c.core.ChangeProperty(xproto.PropMode.Replace, window,
                                 atom('_NET_WM_WINDOW_OPACITY'),
                                 CARDINAL, 32, 1, packed)

def set_wm_window_opacity_checked(window, opacity):
    assert 0 <= opacity <= 1
    packed = struct.pack('I', int(opacity * 0xffffffff))
    return c.core.ChangePropertyChecked(xproto.PropMode.Replace, window,
                                        atom('_NET_WM_WINDOW_OPACITY'),
                                        CARDINAL, 32, 1, packed)

# _NET_WM_DESKTOP

def get_wm_desktop(window):
    """
    Get the desktop index of the window.

    :param window:  A window identifier.
    :return:        The window's virtual desktop index.
    :rtype:         util.PropertyCookieSingle (CARDINAL/32)
    """
    return util.PropertyCookieSingle(util.get_property(window,
                                                       '_NET_WM_DESKTOP'))

def get_wm_desktop_unchecked(window):
    cook = util.get_property_unchecked(window, '_NET_WM_DESKTOP')
    return util.PropertyCookieSingle(cook)

def set_wm_desktop(window, desktop):
    """
    Sets the desktop index of the window.

    :param window:  A window identifier.
    :param desktop: A desktop index.
    :type desktop:  CARDINAL/32
    :rtype:         xcb.VoidCookie
    """
    return c.core.ChangeProperty(xproto.PropMode.Replace, window,
                                 atom('_NET_WM_DESKTOP'),
                                 CARDINAL, 32, 1, [desktop])

def set_wm_desktop_checked(window, desktop):
    return c.core.ChangePropertyChecked(xproto.PropMode.Replace, window,
                                        atom('_NET_WM_DESKTOP'),
                                        CARDINAL, 32, 1, [desktop])

def request_wm_desktop(window, desktop, source=1):
    """
    Sends an event to root window to change the desktop of the window.

    :param window:  A window identifier.
    :param desktop: A desktop index.
    :type desktop:  CARDINAL/32
    :param source:  The source indication.
    :rtype:         xcb.VoidCookie
    """
    return revent(window, '_NET_WM_DESKTOP', desktop, source)

def request_wm_desktop_checked(window, desktop, source=1):
    return revent_checked(window, '_NET_WM_DESKTOP', desktop, source)

# _NET_WM_WINDOW_TYPE

def get_wm_window_type(window):
    """
    Get a list of atoms representing the type of the window.

    :param window:  A window identifier.
    :return:        A list of atoms corresponding to this window's type.
    :rtype:         util.PropertyCookie (ATOM[]/32)
    """
    return util.PropertyCookie(util.get_property(window, '_NET_WM_WINDOW_TYPE'))

def get_wm_window_type_unchecked(window):
    cook = util.get_property_unchecked(window, '_NET_WM_WINDOW_TYPE')
    return util.PropertyCookie(cook)

def set_wm_window_type(window, types):
    """
    Sets the list of atoms representing this window's type.

    :param window:  A window identifier.
    :param types:   A list of window type atoms.
    :type types:    ATOM[]/32
    :rtype:         xcb.VoidCookie
    """
    packed = struct.pack('I' * len(types), *types)
    return c.core.ChangeProperty(xproto.PropMode.Replace, window,
                                 atom('_NET_WM_WINDOW_TYPE'),
                                 ATOM, 32, len(types), packed)

def set_wm_window_type_checked(window, types):
    packed = struct.pack('I' * len(types), *types)
    return c.core.ChangePropertyChecked(xproto.PropMode.Replace, window,
                                        atom('_NET_WM_WINDOW_TYPE'),
                                        ATOM, 32, len(types), packed)

# _NET_WM_STATE

def get_wm_state(window):
    """
    Get a list of atoms representing the state of the window.

    :param window:  A window identifier.
    :return:        A list of atoms corresponding to this window's state.
    :rtype:         util.PropertyCookie (ATOM[]/32)
    """
    return util.PropertyCookie(util.get_property(window, '_NET_WM_STATE'))

def get_wm_state_unchecked(window):
    return util.PropertyCookie(util.get_property_unchecked(window,
                                                           '_NET_WM_STATE'))

def set_wm_state(window, states):
    """
    Sets the list of atoms representing this window's state.

    :param window:  A window identifier.
    :param states:  A list of window state atoms.
    :type states:   ATOM[]/32
    :rtype:         xcb.VoidCookie
    """
    packed = struct.pack('I' * len(states), *states)
    return c.core.ChangeProperty(xproto.PropMode.Replace, window,
                                 atom('_NET_WM_STATE'), ATOM, 32, len(states),
                                 packed)

def set_wm_state_checked(window, states):
    packed = struct.pack('I' * len(states), *states)
    return c.core.ChangePropertyChecked(xproto.PropMode.Replace, window,
                                        atom('_NET_WM_STATE'),
                                        ATOM, 32, len(states), packed)

def request_wm_state(window, action, first, second=0, source=1):
    """
    Sends an event to root window to change the state of the window.

    :param window:  A window identifier.
    :param action:  The kind of state action to perform. I tshould be one
                    of the following flags:

                    _NET_WM_STATE_REMOVE    = 0
                    _NET_WM_STATE_ADD       = 1
                    _NET_WM_STATE_TOGGLE    = 2
    :param first:   The first property to be changed.
    :param second:  The second property to be changed (should be 0 if only
                    one property is being changed).
    :param source:  The source indication.
    :rtype:         xcb.VoidCookie
    """
    return revent(window, '_NET_WM_STATE', action, first, second, source)

def request_wm_state_checked(window, action, first, second=0, source=1):
    return revent_checked(window, '_NET_WM_STATE',
                          action, first, second, source)

# _NET_WM_ALLOWED_ACTIONS

def get_wm_allowed_actions(window):
    """
    Get a list of atoms representing the WM supported actions on a window.

    :param window:  A window identifier.
    :return:        A list of atoms corresponding to this window's supported
                    actions through the window manager.
    :rtype:         util.PropertyCookie (ATOM[]/32)
    """
    return util.PropertyCookie(util.get_property(window,
                                                 '_NET_WM_ALLOWED_ACTIONS'))

def get_wm_allowed_actions_unchecked(window):
    cook = util.get_property_unchecked(window, '_NET_WM_ALLOWED_ACTIONS')
    return util.PropertyCookie(cook)

def set_wm_allowed_actions(window, actions):
    """
    Sets the list of atoms representing the WM supported actions on a window.

    :param window:  A window identifier.
    :param actions:  A list of allowable action atoms.
    :type actions:   ATOM[]/32
    :rtype:         xcb.VoidCookie
    """
    packed = struct.pack('I' * len(actions), *actions)
    return c.core.ChangeProperty(xproto.PropMode.Replace, window,
                                 atom('_NET_WM_ALLOWED_ACTIONS'),
                                 ATOM, 32, len(actions), packed)

def set_wm_allowed_actions_checked(window, actions):
    packed = struct.pack('I' * len(actions), *actions)
    return c.core.ChangePropertyChecked(xproto.PropMode.Replace, window,
                                        atom('_NET_WM_ALLOWED_ACTIONS'),
                                        ATOM, 32, len(actions), packed)

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

def get_wm_strut(window):
    """
    Returns the struts for a window.

    :param window:  A window identifier.
    :return:        A strut dictionary.

                    Keys: left, right, top, bottom
    :rtype:         StrutCookie (CARDINAL[4]/32)
    """
    return StrutCookie(util.get_property(window, '_NET_WM_STRUT'))

def get_wm_strut_unchecked(window):
    return StrutCookie(util.get_property_unchecked(window, '_NET_WM_STRUT'))

def set_wm_strut(window, left, right, top, bottom):
    """
    Sets the struts for a window.

    :param window:  A window identifier.
    :param left:    Width of area at left side of screen.
    :type left:     CARDINAL/32
    :param right:   Width of area at right side of screen.
    :type right:    CARDINAL/32
    :param top:     Height of area at top side of screen.
    :type top:      CARDINAL/32
    :param bottom:  Height of area at bottom side of screen.
    :type bottom:   CARDINAL/32
    :rtype:         xcb.VoidCookie
    """
    packed = struct.pack('IIII', left, right, top, bottom)
    return c.core.ChangeProperty(xproto.PropMode.Replace, window,
                                 atom('_NET_WM_STRUT'), CARDINAL, 32, 4, packed)

def set_wm_strut_checked(window, left, right, top, bottom):
    packed = struct.pack('IIII', left, right, top, bottom)
    return c.core.ChangePropertyChecked(xproto.PropMode.Replace, window,
                                        atom('_NET_WM_STRUT'),
                                        CARDINAL, 32, 4, packed)

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

def get_wm_strut_partial(window):
    """
    Returns the partial struts for a window.

    :param window:  A window identifier.
    :return:        A strut dictionary.

                    Keys: left, right, top, bottom, left_start_y, left_end_y,
                    right_start_y, right_end_y, top_start_x, top_end_x,
                    bottom_start_x, bottom_end_x
    :rtype:         StrutPartialCookie (CARDINAL[12]/32)
    """
    return StrutPartialCookie(util.get_property(window,
                                                '_NET_WM_STRUT_PARTIAL'))

def get_wm_strut_partial_unchecked(window):
    cook = util.get_property_unchecked(window, '_NET_WM_STRUT_PARTIAL')
    return StrutPartialCookie(cook)

def set_wm_strut_partial(window, left, right, top, bottom, left_start_y,
                         left_end_y, right_start_y, right_end_y, top_start_x,
                         top_end_x, bottom_start_x, bottom_end_x):
    """
    Sets the partial struts for a window.

    :param window:          A window identifier.
    :param left:            Width of area at left side of screen.
    :type left:             CARDINAL/32
    :param right:           Width of area at right side of screen.
    :type right:            CARDINAL/32
    :param top:             Height of area at top side of screen.
    :type top:              CARDINAL/32
    :param bottom:          Height of area at bottom side of screen.
    :type bottom:           CARDINAL/32
    :param left_start_y:
    :param left_end_y:
    :param right_start_y:
    :param right_end_y:
    :param top_start_x:
    :param top_end_x:
    :param bottom_start_x:
    :param bottom_end_x:
    :rtype:                 xcb.VoidCookie
    """
    packed = struct.pack('I' * 12, left, right, top, bottom, left_start_y,
                         left_end_y, right_start_y, right_end_y, top_start_x,
                         top_end_x, bottom_start_x, bottom_end_x)
    return c.core.ChangeProperty(xproto.PropMode.Replace, window,
                                 atom('_NET_WM_STRUT_PARTIAL'),
                                 CARDINAL, 32, 12, packed)

def set_wm_strut_partial_checked(window, left, right, top, bottom,
                                 left_start_y, left_end_y, right_start_y,
                                 right_end_y, top_start_x, top_end_x,
                                 bottom_start_x, bottom_end_x):
    packed = struct.pack('I' * 12, left, right, top, bottom, left_start_y,
                         left_end_y, right_start_y, right_end_y, top_start_x,
                         top_end_x, bottom_start_x, bottom_end_x)
    return c.core.ChangePropertyChecked(xproto.PropMode.Replace, window,
                                        atom('_NET_WM_STRUT_PARTIAL'),
                                        CARDINAL, 32, 12, packed)

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

def get_wm_icon_geometry(window):
    """
    Returns the icon geometry for a window.

    :param window:  A window identifier.
    :return:        An icon geometry dictionary.

                    Keys: x, y, width, height
    :rtype:         IconGeometryCookie (CARDINAL[4]/32)
    """
    return IconGeometryCookie(util.get_property(window,
                                                '_NET_WM_ICON_GEOMETRY'))

def get_wm_icon_geometry_unchecked(window):
    cook = util.get_property_unchecked(window, '_NET_WM_ICON_GEOMETRY')
    return IconGeometryCookie(cook)

def set_wm_icon_geometry(window, x, y, width, height):
    """
    Sets the icon geometry for a window.

    :param window:  A window identifier.
    :param x:       x coordinate of icon area.
    :type x:        CARDINAL/32
    :param y:       y coordinate of icon area.
    :type y:        CARDINAL/32
    :param width:   Width of icon area.
    :type width:    CARDINAL/32
    :param height:  Height of icon area.
    :type height:   CARDINAL/32
    :rtype:         xcb.VoidCookie
    """
    packed = struct.pack('IIII', x, y, width, height)
    return c.core.ChangeProperty(xproto.PropMode.Replace, window,
                                 atom('_NET_WM_ICON_GEOMETRY'),
                                 CARDINAL, 32, 4, packed)

def set_wm_icon_geometry_checked(window, x, y, width, height):
    packed = struct.pack('IIII', x, y, width, height)
    return c.core.ChangePropertyChecked(xproto.PropMode.Replace, window,
                                        atom('_NET_WM_ICON_GEOMETRY'),
                                        CARDINAL, 32, 4, packed)

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

def get_wm_icon(window):
    """
    Returns an array of possible icons for a window.

    :param window:  A window identifier.
    :return:        A list of icon dictionaries.

                    Keys: width, height, data
    :rtype:         IconCookie (CARDINAL[][2+n]/32)
    """
    return IconCookie(util.get_property(window, '_NET_WM_ICON'))

def get_wm_icon_unchecked(window):
    return IconCookie(util.get_property_unchecked(window, '_NET_WM_ICON'))

def set_wm_icon(window, icons):
    """
    Sets the array of possible icons for a window.

    :param window:  A window identifier.
    :param icons:   A list icon dictionaries. Each dictionary should have
                    the following keys: width, height and data.
    :type icons:    CARDINAL[][2+n]/32
    :rtype:         xcb.VoidCookie
    """
    flatten = []
    for icon in icons:
        flatten.append(icon['width'])
        flatten.append(icon['height'])
        for argb in icon['data']:
            flatten.append(argb)
    packed = struct.pack('I' * len(flatten), *flatten)

    return c.core.ChangeProperty(xproto.PropMode.Replace, window,
                                 atom('_NET_WM_ICON'),
                                 CARDINAL, 32, len(flatten), packed)

def set_wm_icon_checked(window, icons):
    flatten = []
    for icon in icons:
        flatten.append(icon['width'])
        flatten.append(icon['height'])
        for argb in icon['data']:
            flatten.append(argb)
    packed = struct.pack('I' * len(flatten), *flatten)

    return c.core.ChangePropertyChecked(xproto.PropMode.Replace, window,
                                        atom('_NET_WM_ICON'),
                                        CARDINAL, 32, len(flatten), packed)

# _NET_WM_PID

def get_wm_pid(window):
    """
    Get the process ID of the client owning a window.

    :param window:  A window identifier.
    :return:        The window's client's process ID.
    :rtype:         util.PropertyCookieSingle (CARDINAL/32)
    """
    return util.PropertyCookieSingle(util.get_property(window, '_NET_WM_PID'))

def get_wm_pid_unchecked(window):
    cook = util.get_property_unchecked(window, '_NET_WM_PID')
    return util.PropertyCookieSingle(cook)

def set_wm_pid(window, pid):
    """
    Sets the process ID of the client owning a window.

    :param window:  A window identifier.
    :param pid:     A process ID.
    :type pid:      CARDINAL/32
    :rtype:         xcb.VoidCookie
    """
    packed = struct.pack('I', pid)
    return c.core.ChangeProperty(xproto.PropMode.Replace, window,
                                 atom('_NET_WM_PID'), CARDINAL, 32, 1,
                                 packed)

def set_wm_pid_checked(window, pid):
    packed = struct.pack('I', pid)
    return c.core.ChangePropertyChecked(xproto.PropMode.Replace, window,
                                        atom('_NET_WM_PID'), CARDINAL, 32, 1,
                                        packed)

# _NET_WM_HANDLED_ICONS

def get_wm_handled_icons(window):
    """
    Gets the "handled icons" property.

    :param window:  A window identifier.
    :return:        Whether this property is set or not.
    :rtype:         util.PropertyCookieSingle (CARDINAL/32)
    """
    return util.PropertyCookieSingle(util.get_property(window,
                                                       '_NET_WM_HANDLED_ICONS'))

def get_wm_handled_icons_unchecked(window):
    cook = util.get_property_unchecked(window, '_NET_WM_HANDLED_ICONS')
    return util.PropertyCookieSingle(cook)

def set_wm_handled_icons(window):
    """
    Sets the "handled icons" property.

    :param window:  A window identifier.
    :return:        Whether this property is set or not.
    :rtype:         xcb.VoidCookie
    """
    return c.core.ChangeProperty(xproto.PropMode.Replace, window,
                                 atom('_NET_WM_HANDLED_ICONS'), CARDINAL, 32, 1,
                                 [1])

def set_wm_handled_icons_checked(window):
    return c.core.ChangePropertyChecked(xproto.PropMode.Replace, window,
                                        atom('_NET_WM_HANDLED_ICONS'),
                                        CARDINAL, 32, 1, [1])

# _NET_WM_USER_TIME

def get_wm_user_time(window):
    """
    Get the time at which the last user activity occurred on a window.

    :param window:  A window identifier.
    :return:        The XServer time when user activity last occurred.
    :rtype:         util.PropertyCookieSingle (CARDINAL/32)
    """
    return util.PropertyCookieSingle(util.get_property(window,
                                                       '_NET_WM_USER_TIME'))

def get_wm_user_time_unchecked(window):
    cook = util.get_property_unchecked(window, '_NET_WM_USER_TIME')
    return util.PropertyCookieSingle(cook)

def set_wm_user_time(window, user_time):
    """
    Sets the time that user activity last occurred on this window.

    :param window:      A window identifier.
    :param user_time:   Last user activity time.
    :type user_time:    CARDINAL/32
    :rtype:             xcb.VoidCookie
    """
    return c.core.ChangeProperty(xproto.PropMode.Replace, window,
                                 atom('_NET_WM_USER_TIME'), CARDINAL, 32, 1,
                                 [user_time])

def set_wm_user_time_checked(window, user_time):
    return c.core.ChangePropertyChecked(xproto.PropMode.Replace, window,
                                        atom('_NET_WM_USER_TIME'),
                                        CARDINAL, 32, 1, [user_time])

# _NET_WM_USER_TIME_WINDOW

def get_wm_user_time_window(window):
    """
    Gets the window that sets the _NET_WM_USER_TIME property.

    :param window:  A window identifier.
    :return:        Window identifier that sets the _NET_WM_USER_TIME property.
    :rtype:         util.PropertyCookieSingle (WINDOW/32)
    """
    cook = util.get_property(window, '_NET_WM_USER_TIME_WINDOW')
    return util.PropertyCookieSingle(cook)

def get_wm_user_time_window_unchecked(window):
    cook = util.get_property_unchecked(window, '_NET_WM_USER_TIME_WINDOW')
    return util.PropertyCookieSingle(cook)

def set_wm_user_time_window(window, time_win):
    """
    Sets the window identifier that sets the _NET_WM_USER_TIME property.

    :param window:      A window identifier.
    :param time_win:    Window ID that sets the _NET_WM_USER_TIME property.
    :type time_win:     WINDOW/32
    :rtype:             xcb.VoidCookie
    """
    return c.core.ChangeProperty(xproto.PropMode.Replace, window,
                                 atom('_NET_WM_USER_TIME_WINDOW'),
                                 WINDOW, 32, 1, [time_win])

def set_wm_user_time_window_checked(window, time_win):
    return c.core.ChangePropertyChecked(xproto.PropMode.Replace, window,
                                        atom('_NET_WM_USER_TIME_WINDOW'),
                                        WINDOW, 32, 1, [time_win])

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

def get_frame_extents(window):
    """
    Returns the frame extents for a window.

    :param window:  A window identifier.
    :return:        A frame extents dictionary.

                    Keys: left, right, top, bottom
    :rtype:         FrameExtentsCookie (CARDINAL[4]/32)
    """
    return FrameExtentsCookie(util.get_property(window, '_NET_FRAME_EXTENTS'))

def get_frame_extents_unchecked(window):
    cook = util.get_property_unchecked(window, '_NET_FRAME_EXTENTS')
    return FrameExtentsCookie(cook)

def set_frame_extents(window, left, right, top, bottom):
    """
    Sets the frame extents for a window.

    :param window:  A window identifier.
    :param left:    Width of left border.
    :type left:     CARDINAL/32
    :param right:   Width of right border.
    :type right:    CARDINAL/32
    :param top:     Height of top border.
    :type top:      CARDINAL/32
    :param bottom:  Height of bottom border.
    :type bottom:   CARDINAL/32
    :rtype:         xcb.VoidCookie
    """
    packed = struct.pack('IIII', left, right, top, bottom)
    return c.core.ChangeProperty(xproto.PropMode.Replace, window,
                                 atom('_NET_FRAME_EXTENTS'), CARDINAL, 32, 4,
                                 packed)

def set_frame_extents_checked(window, left, right, top, bottom):
    packed = struct.pack('IIII', left, right, top, bottom)
    return c.core.ChangePropertyChecked(xproto.PropMode.Replace, window,
                                        atom('_NET_FRAME_EXTENTS'),
                                        CARDINAL, 32, 4, packed)

# _NET_WM_PING

def request_wm_ping(window, response=False,
                    timestamp=xproto.Time.CurrentTime):
    """
    Sends an event to root window to ping a window or respond to a ping.

    :param window:      A window identifier.
    :param response:    Whether this is a response to a ping request or not.
    :type timestamp:    Milliseconds
    :rtype:             xcb.VoidCookie
    """
    return revent(window if not response else root(c),
                  'WM_PROTOCOLS', atom('_NET_WM_PING'), timestamp, window)

def request_wm_ping_checked(window, response=False,
                            timestamp=xproto.Time.CurrentTime):
    return revent_checked(window if not response else root(c), 'WM_PROTOCOLS',
                          atom('_NET_WM_PING'), timestamp, window)

# _NET_WM_SYNC_REQUEST

def request_wm_sync_request(window, req_num,
                            timestamp=xproto.Time.CurrentTime):
    """
    Sends an event to root window to sync with a client.

    :param window:      A window identifier.
    :param req_num:     The XSync request number.
    :type timestamp:    Milliseconds
    :rtype:             xcb.VoidCookie
    """
    high = req_num >> 32
    low = (high << 32) ^ req_num

    return revent(window, 'WM_PROTOCOLS',
                  atom('_NET_WM_SYNC_REQUEST'), timestamp, low, high)

def request_wm_sync_request_checked(window, req_num,
                                    timestamp=xproto.Time.CurrentTime):
    high = req_num >> 32
    low = (high << 32) ^ req_num

    return revent_checked(window, 'WM_PROTOCOLS',
                          atom('_NET_WM_SYNC_REQUEST'), timestamp, low, high)

# _NET_WM_SYNC_REQUEST_COUNTER

def get_wm_sync_request_counter(window):
    """
    Gets XSync counter for this client.

    :param window:  A window identifier.
    :return:        An XSync XID.
    :rtype:         util.PropertyCookieSingle (CARDINAL/32)
    """
    cook = util.get_property(window, '_NET_WM_SYNC_REQUEST_COUNTER')
    return util.PropertyCookieSingle(cook)

def get_wm_sync_request_counter_unchecked(window):
    cook = util.get_property_unchecked(window, '_NET_WM_SYNC_REQUEST_COUNTER')
    return util.PropertyCookieSingle(cook)

def set_wm_sync_request_counter(window, counter):
    """
    Sets the XSync counter for this client.

    :param window:      A window identifier.
    :param counter:     An XSync XID.
    :type counter:      CARDINAL
    :rtype:             xcb.VoidCookie
    """
    packed = struct.pack('I', counter)
    return c.core.ChangeProperty(xproto.PropMode.Replace, window,
                                 atom('_NET_WM_SYNC_REQUEST_COUNTER'),
                                 CARDINAL, 32, 1, packed)

def set_wm_sync_request_counter_checked(window, counter):
    packed = struct.pack('I', counter)
    return c.core.ChangePropertyChecked(xproto.PropMode.Replace, window,
                                        atom('_NET_WM_SYNC_REQUEST_COUNTER'),
                                        CARDINAL, 32, 1, packed)

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

def get_wm_fullscreen_monitors(window):
    """
    Get list of monitor edges for this window.

    :param window:  A window identifier.
    :return:        The window's monitor edges.
    :rtype:         FullscreenMonitorsCookie (CARDINAL[4]/32)
    """
    return FullscreenMonitorsCookie(
        util.get_property(window, '_NET_WM_FULLSCREEN_MONITORS'))

def get_wm_fullscreen_monitors_unchecked(window):
    cook = util.get_property_unchecked(window, '_NET_WM_FULLSCREEN_MONITORS')
    return FullscreenMonitorsCookie(cook)

def set_wm_fullscreen_monitors(window, top, bottom, left, right):
    """
    Sets list of monitor edges for this window.

    :param window:  A window identifier.
    :param top:     The monitor whose top edge defines the top edge of window.
    :param bottom:  The monitor whose bottom edge defines the bottom edge of
                    window.
    :param left:    The monitor whose left edge defines the left edge of
                    window.
    :param right:   The monitor whose right edge defines the right edge of
                    window.
    :rtype:         xcb.VoidCookie
    """
    packed = struct.pack('IIII', top, bottom, left, right)
    return c.core.ChangeProperty(xproto.PropMode.Replace, window,
                                 atom('_NET_WM_FULLSCREEN_MONITORS'),
                                 CARDINAL, 32, 4, packed)

def set_wm_fullscreen_monitors_checked(window, top, bottom, left, right):
    packed = struct.pack('IIII', top, bottom, left, right)
    return c.core.ChangePropertyChecked(xproto.PropMode.Replace, window,
                                        atom('_NET_WM_FULLSCREEN_MONITORS'),
                                        CARDINAL, 32, 4, packed)

def request_wm_fullscreen_monitors(window, top, bottom, left, right,
                                   source=1):
    """
    Sends an event to root window to change monitor edges for this window.

    :param window:  A window identifier.
    :param top:     The monitor whose top edge defines the top edge of window.
    :param bottom:  The monitor whose bottom edge defines the bottom edge of
                    window.
    :param left:    The monitor whose left edge defines the left edge of
                    window.
    :param right:   The monitor whose right edge defines the right edge of
                    window.
    :param source:  The source indication.
    :rtype:         xcb.VoidCookie
    """
    return revent(window, '_NET_WM_FULLSCREEN_MONITORS',
                  top, bottom, left, right, source)

def request_wm_fullscreen_monitors_checked(window, top, bottom, left, right,
                                           source=1):
    return revent_checked(window, '_NET_WM_FULLSCREEN_MONITORS',
                          top, bottom, left, right, source)

