import xcb.xinerama

from xpybutil import conn
import util

ext = conn(xcb.xinerama.key)

def get_monitors():
    '''
    Returns a list of Xinerama screen rectangles.
    They come in the order that the Xinerama extension specifies.

    @rtype: List of (x, y, w, h) rectangles
    '''
    retval = []
    ms = ext.QueryScreens().reply()
    if ms:
        for m in ms.screen_info:
            retval.append((m.x_org, m.y_org, m.width, m.height))

    return retval

def get_physical_mapping(monitors):
    '''
    Returns a list of Xinerama screen indices in their physical order.

    @param monitors:  List of (x, y, w, h) rectangles
    @rtype:           List of Xinerama indices
    '''
    retval = []

    tosort = []
    for i, (x, y, w, h) in enumerate(monitors):
        tosort.append((y, x, i))
    for x, y, xscreen in sorted(tosort):
        retval.append(xscreen)

    return retval

