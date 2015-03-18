Introduction
============
xpybutil is an abstraction over the X Python Binding (xpyb - the Python version
of XCB). It exists because xpyb is a very low level library that communicates
with X.

The most mature portions of xpybutil are the ICCCM and EWMH modules. Each
implement their respective specifications of the same name. The EWMH module
also implements the '_NET_WM_WINDOW_OPACITY' and '_NET_VISIBLE_DESKTOPS'
non-standard features. The former is widely used by compositing managers and
other utilities (i.e., xcompmgr and transset-df) while the latter is used by my
fork of Openbox called Openbox Multihead.


Documentation
=============
The API docs can be found here: http://pdoc.burntsushi.net/xpybutil


Examples
========
There are a few examples included in the 'examples' directory of the source of
xpybutil. You could also look at my 'window-marker' or 'pytyle3' utilities. The
former is a small script but the latter is on the order of ~1000 lines and
encompasses a wide variety of use cases of xpybutil. (And still yet, other use
cases are probably more appropriate only for window manager development.)

Another program that uses xpybutil is 'pager-multihead'. I would advise not
looking to it for inspiration, as it mixes xpybutil and GTK. (Namely, it uses
GTK's event dispatcher, but interacts with the window manager mostly using
xpybutil.)


Usable modules
==============
cursor.py    - Provides a listing of all built-in X cursors, and provides a
               function 'create_font_cursor' to create one. This object can
               then be directly used in a call to CreateWindow or
               ChangeWindowAttributes.

ewmh.py      - A module that implements the entire EWMH spec.

event.py     - A module that can send client events to windows. It also allows
               registering callback functions to particular events. It can also
               run the main event loop.

icccm.py     - A module that implements most of the ICCCM spec.

image.py     - An incomplete and haphazard collection of functions that can
               bridge a gap between PIL and drawing images with X.

keybind.py   - A set of functions devoted to binding key presses and registering
               callbacks. This will automatically hook into the event callbacks
               in event.py.

keysymdef.py - The sole purpose of this module is to provide a mapping from
               X keysyms to english string representations (for easier binding
               by the user). This should probably never be used directly. It is
               used by the keysym module.

motif.py     - Implements a subset of the Motif spec. This module exists
               because some window managers still use this as the only way of
               toggling window decorations via events.

mousebind.py - Similar to keybind.py, but for mice.

rect.py      - A few utility functions that do math associated with X style
               rectangles. (i.e., a 4-tuple of (top_left_x, top_left_y, width,
               height).) It can also calculate monitor rectangles after
               accounting for struts.

render.py    - A nearly exact port of the module by the same name from
               xcb-util. I used it once to help with a compositing manager that
               I wrote with xpyb.

util.py      - A vast assortment of utility functions. The ones of interest to
               you are probably 'get_atom' and 'get_atom_name'. The rest are
               heavily used throughout the rest of xpybutil.

window.py    - A few utility functions related to client windows. In
               particular, getting an accurate geometry of a client window
               including the decorations (this can vary with the window
               manager). Also, a functon to move and/or resize a window
               accurately by the top-left corner. (Also can change based on
               the currently running window manager.)

               This module also contains a function 'listen' that must be used
               in order to receive certain events from a window. For example,
               if you wanted to run 'func' whenever a property on the root
               window changed, you could do something like:

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

xinerama.py  - A couple of functions that support retrieving information about
               all active physical heads. This is done through the Xinerama
               extension, which implicitly supports RandR and TwinView.

               The 'get_physical_mapping' function will produce a list of
               monitor indices in a physical ordering (left to right, top to
               bottom). These indices can then be used in the list returned by
               'get_monitors'.


Unusable modules
================
font.py is pretty inadequate. Mostly because if you find
yourself wanting to use font.py, you're probably doing something wrong.
(i.e., use pycairo or PIL.)


EWMH and ICCCM
==============
xpybutil's primary purpose was to make accessing ICCCM and EWMH related
information extremely easy. This can be done by using the ewmh or icccm
modules. Here's a quick example (assuming xpybutil is installed):

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

  import xpybutil.ewmh as ewmh

  print ewmh.get_wm_strut_partial(ID).reply()

Which outputs a dictionary with 12 entries, where each corresponds to a value
in the partial strut. (i.e., 'left', 'top_end_x', 'right_start_y', etc...).

In general, particularly with the EWMH module, the ewmh module is very nearly
representative of the spec itself. Functions that get property values start
with 'get_', functions that set property values start with 'set_', and
functions that send an event to a client (which typically requests the window
manager to DO something) start with 'request_'.

If a request has no reply (typically the 'set_' functions), then the
default is to call it 'unchecked'. If you want to check the result (and force
retrieval), then use the '_checked' variant.

The reverse goes for the 'get_' functions. By default, they are checked, but
you can use the '_unchecked' variant too.

Basically, you should probably almost always use the 'checked' variant of
everything. The cases where you don't are when you want to send a whole bunch
of requests to the X server at once. You could use the unchecked invariant, and
after you've initialized all the cookies, calling 'flush' will force
communication with the X server.

Finally, unless you're writing a window manager or creating a client window
from scratch, you'll almost always want to use the 'get_' and 'request_'
functions, not 'set_'. For example, if you want to change the current
desktop...

  DON'T DO: ewmh.set_current_desktop_checked(2).check()

  DO:       ewmh.request_current_desktop_checked(2).check()

The former will probably not work, but the latter will. Just follow the EWMH
spec :-)
