import xcb, xcb.xproto
conn = xcb.connect()
root = conn.get_setup().roots[0].root

