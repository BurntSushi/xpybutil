import xcb, xcb.xproto

try:
    conn = xcb.connect()
    root = conn.get_setup().roots[0].root
except xcb.ConnectException:
    conn = None
    root = None

