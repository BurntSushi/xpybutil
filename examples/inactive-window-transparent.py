# Makes all inactive windows transparent and keeps the active window opaque.

# Range of values: 0 <= opacity <= 1
# where 1 is fully opaque and 0 is completely invisible
opacity = 0.8

import xcb

from xpybutil import conn, root
import xpybutil.event as event
import xpybutil.ewmh as ewmh
import xpybutil.util as util

conn.core.ChangeWindowAttributes(root, xcb.xproto.CW.EventMask,
                                 [xcb.xproto.EventMask.PropertyChange])
conn.flush()

get_atom = util.get_atom
get_parent = util.get_parent_window
get_active = ewmh.get_active_window
set_opacity = ewmh.set_wm_window_opacity

def update_window_opacity():
    activewin = get_active(conn, root).reply()
    if not activewin:
        return

    for client in clients:
        set_opacity(conn, get_parent(conn, client), 
                    1 if client == activewin else opacity)

    conn.flush()

def client_is_normal(client):
    wtype = ewmh.get_wm_window_type(conn, client).reply()
    if not wtype or wtype[0] == get_atom(conn, '_NET_WM_WINDOW_TYPE_NORMAL'):
        return True
    return False

clients = filter(client_is_normal, ewmh.get_client_list(conn, root).reply())
update_window_opacity()

while True:
    event.read(conn, block=True)
    for e in event.queue():
        if not isinstance(e, xcb.xproto.PropertyNotifyEvent):
            continue

        aname = util.get_atom_name(conn, e.atom)
        if aname == '_NET_ACTIVE_WINDOW':
            update_window_opacity()
        elif aname == '_NET_CLIENT_LIST':
            clients = filter(client_is_normal, 
                             ewmh.get_client_list(conn, root).reply())

