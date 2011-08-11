from xpybutil import conn, root
import xpybutil.ewmh as ewmh

names = ewmh.get_desktop_names(conn, root).reply()
desk = ewmh.get_current_desktop(conn, root).reply()

print names[desk] if desk < len(names) else desk

