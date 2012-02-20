import xcb.xproto

import xpybutil.ewmh as ewmh
import xpybutil.window as window

def rect_intersect_area(r1, r2):
    '''
    Returns the area of the intersection of two rectangles. If the rectangles
    do not intersect, the area returned is 0.

    @param r1: A 4-tuple representing a rectangle:
               (top_left_x, top_left_y, width, height)
    @param r2: A 4-tuple representing a rectangle:
               (top_left_x, top_left_y, width, height)
    @return: Area of intersection of r1 and r2.
    @rtype:  Integer
    '''
    x1, y1, w1, h1 = r1
    x2, y2, w2, h2 = r2
    if x2 < x1 + w1 and x2 + w2 > x1 and y2 < y1 + h1 and y2 + h2 > y1:
        iw = min(x1 + w1 - 1, x2 + w2 - 1) - max(x1, x2) + 1
        ih = min(y1 + h1 - 1, y2 + h2 - 1) - max(y1, y2) + 1
        return iw * ih

    return 0

