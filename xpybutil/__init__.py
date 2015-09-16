from xpybutil.compat import xcb, xcb_ConnectException

try:
    conn = xcb.connect()
    root = conn.get_setup().roots[0].root
except xcb_ConnectException:
    conn = None
    root = None
