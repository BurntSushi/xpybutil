# Makes all inactive windows transparent and keeps the active window opaque.
# This should be run in the background as a daemon like so:
# python2 inactive-window-transparent.py

# Range of values: 0 <= opacity <= 1
# where 1 is fully opaque and 0 is completely invisible
opacity = 0.8

import xpybutil
import xpybutil.event as event
import xpybutil.ewmh as ewmh
import xpybutil.util as util
import xpybutil.window as window

def update_window_opacity():
    activewin = ewmh.get_active_window().reply()
    if not activewin:
        return

    for client in clients:
        ewmh.set_wm_window_opacity(util.get_parent_window(client), 
                                   1 if client == activewin else opacity)

    xpybutil.conn.flush()

def client_is_normal(client):
    wtype = ewmh.get_wm_window_type(client).reply()
    if not wtype or wtype[0] == util.get_atom('_NET_WM_WINDOW_TYPE_NORMAL'):
        return True
    return False

def cb_property_notify(e):
    global clients

    aname = util.get_atom_name(e.atom)

    if aname == '_NET_ACTIVE_WINDOW':
        update_window_opacity();
    elif aname == '_NET_CLIENT_LIST':
        clients = filter(client_is_normal, ewmh.get_client_list().reply())

clients = filter(client_is_normal, ewmh.get_client_list().reply())
update_window_opacity()

window.listen(xpybutil.root, 'PropertyChange')
event.connect('PropertyNotify', xpybutil.root, cb_property_notify)

event.main()

