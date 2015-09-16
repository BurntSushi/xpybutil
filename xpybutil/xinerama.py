"""
A couple of functions that support retrieving information about
all active physical heads. This is done through the Xinerama
extension, which implicitly supports RandR and TwinView.

The 'get_physical_mapping' function will produce a list of
monitor indices in a physical ordering (left to right, top to
bottom). These indices can then be used in the list returned by
'get_monitors'.
"""
from xpybutil.compat import xinerama

from xpybutil import conn

ext = None
if conn is not None:
    ext = conn(xinerama.key)

def get_monitors():
    '''
    Returns a list of Xinerama screen rectangles.
    They come in the order that the Xinerama extension specifies.

    :rtype: List of (x, y, w, h) rectangles
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
    Where physical order is defined as left-to-right and then top-to-bottom.

    :param monitors:  List of (x, y, w, h) rectangles
    :rtype:           List of Xinerama indices
    '''
    retval = []

    tosort = []
    for i, (x, y, w, h) in enumerate(monitors):
        tosort.append((x, y, i))
    for x, y, xscreen in sorted(tosort):
        retval.append(xscreen)

    return retval

