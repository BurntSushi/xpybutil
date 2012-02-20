import xpybutil.ewmh as ewmh

names = ewmh.get_desktop_names().reply()
desk = ewmh.get_current_desktop().reply()

print names[desk] if desk < len(names) else desk

