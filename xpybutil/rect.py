"""
This module has a few utility functions that perform math on rectangles.

For example, finding the area of intersection of two rectangles with
``rect_intersect_area``, or getting the rectangle of a monitor after accounting
for struts with ``monitor_rects``.
"""
from xpybutil.compat import xproto

import xpybutil.ewmh as ewmh
import xpybutil.window as window

def rect_intersect_area(r1, r2):
    """
    Returns the area of the intersection of two rectangles. If the rectangles
    do not intersect, the area returned is 0.

    :param r1: A 4-tuple representing a rectangle:

               (top_left_x, top_left_y, width, height)
    :param r2: A 4-tuple representing a rectangle:

               (top_left_x, top_left_y, width, height)
    :return: Area of intersection of r1 and r2.
    :rtype:  Integer
    """
    x1, y1, w1, h1 = r1
    x2, y2, w2, h2 = r2
    if x2 < x1 + w1 and x2 + w2 > x1 and y2 < y1 + h1 and y2 + h2 > y1:
        iw = min(x1 + w1 - 1, x2 + w2 - 1) - max(x1, x2) + 1
        ih = min(y1 + h1 - 1, y2 + h2 - 1) - max(y1, y2) + 1
        return iw * ih

    return 0

def get_monitor_area(search, monitors):
    """
    Returns the monitor with the most overlap with the 'search' rectangle.

    :param search: A 4-tuple representing a rectangle:
                   (top_left_x, top_left_y, width, height)
    :param monitors: A list of 4-tuples representing each monitor's rectangle.
    :return: The monitor rectangle with the most overlap with 'search'.
    :rtype: (top_left_x, top_left_y, width, height)
    """
    marea = 0
    mon = None
    for mx, my, mw, mh in monitors:
        a = rect_intersect_area((mx, my, mw, mh), search)
        if a > marea:
            marea = a
            mon = (mx, my, mw, mh)

    return mon

def monitor_rects(monitors):
    """
    Takes a list of monitors returned by ``xinerama.get_monitors`` and returns
    a new list of rectangles, in the same order, of monitor areas that account
    for all struts set by all windows. Duplicate struts are ignored.

    :param monitors: A list of 4-tuples representing monitor rectangles.
    :return: A list of 4-tuples representing monitor rectangles after
             subtracting strut areas.
    :rtype: [(top_left_x, top_left_y, width, height)]
    """
    mons = monitors # alias
    wa = mons[:]

    clients = ewmh.get_client_list().reply()

    log = [] # Identical struts should be ignored

    for c in clients:
        try:
            cx, cy, cw, ch = window.get_geometry(c)
        except xproto.BadWindow:
            continue

        for i, (x, y, w, h) in enumerate(wa):
            if rect_intersect_area((x, y, w, h), (cx, cy, cw, ch)) > 0:
                struts = ewmh.get_wm_strut_partial(c).reply()
                if not struts:
                    struts = ewmh.get_wm_strut(c).reply()

                key = (cx, cy, cw, ch, struts)
                if key in log:
                    continue
                log.append(key)

                if struts and not all([v == 0 for v in struts.itervalues()]):
                    if struts['left'] or struts['right']:
                        if struts['left']:
                            x += cw
                        w -= cw
                    if struts['top'] or struts['bottom']:
                        if struts['top']:
                            y += ch
                        h -= ch
                elif struts:
                    # x/y shouldn't be zero
                    if cx > 0 and w == cx + cw:
                        w -= cw
                    elif cy > 0 and h == cy + ch:
                        h -= ch
                    elif cx > 0 and x == cx:
                        x += cw
                        w -= cw
                    elif cy > 0 and y == cy:
                        y += ch
                        h -= ch

                wa[i] = (x, y, w, h)

    return wa

