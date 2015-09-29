"""
A module that can send client events to windows. It also allows
registering callback functions to particular events. It can also
run the main event loop.
"""
from collections import defaultdict, deque
import struct
import sys
import traceback

from xpybutil.compat import xcb_Exception, xproto

from xpybutil import conn, root, util

__queue = deque()
__callbacks = defaultdict(list)
EM = xproto.EventMask

stringtype = str if sys.version_info[0] >= 3 else basestring

class Event(object):
    KeyPressEvent = 2
    KeyReleaseEvent = 3
    ButtonPressEvent = 4
    ButtonReleaseEvent = 5
    MotionNotifyEvent = 6
    EnterNotifyEvent = 7
    LeaveNotifyEvent = 8
    FocusInEvent = 9
    FocusOutEvent = 10
    KeymapNotifyEvent = 11
    ExposeEvent = 12
    GraphicsExposureEvent = 13
    NoExposureEvent = 14
    VisibilityNotifyEvent = 15
    CreateNotifyEvent = 16
    DestroyNotifyEvent = 17
    UnmapNotifyEvent = 18
    MapNotifyEvent = 19
    MapRequestEvent = 20
    ReparentNotifyEvent = 21
    ConfigureNotifyEvent = 22
    ConfigureRequestEvent = 23
    GravityNotifyEvent = 24
    ResizeRequestEvent = 25
    CirculateNotifyEvent = 26
    CirculateRequestEvent = 27
    PropertyNotifyEvent = 28
    SelectionClearEvent = 29
    SelectionRequestEvent = 30
    SelectionNotifyEvent = 31
    ColormapNotifyEvent = 32
    ClientMessageEvent = 33
    MappingNotifyEvent = 34

def replay_pointer():
    conn.core.AllowEventsChecked(xproto.Allow.ReplayPointer,
                                 xproto.Time.CurrentTime).check()

def send_event(destination, event_mask, event, propagate=False):
    return conn.core.SendEvent(propagate, destination, event_mask, event)

def send_event_checked(destination, event_mask, event, propagate=False):
    return conn.core.SendEventChecked(propagate, destination, event_mask, event)

def pack_client_message(window, message_type, *data):
    assert len(data) <= 5

    if isinstance(message_type, stringtype):
        message_type = util.get_atom(message_type)

    data = list(data)
    data += [0] * (5 - len(data))

    # Taken from
    # http://xcb.freedesktop.org/manual/structxcb__client__message__event__t.html
    return struct.pack('BBH7I', Event.ClientMessageEvent, 32, 0, window,
                       message_type, *data)

def root_send_client_event(window, message_type, *data):
    mask = EM.SubstructureNotify | EM.SubstructureRedirect
    packed = pack_client_message(window, message_type, *data)
    return send_event(root, mask, packed)

def root_send_client_event_checked(window, message_type, *data):
    mask = EM.SubstructureNotify | EM.SubstructureRedirect
    packed = pack_client_message(window, message_type, *data)
    return send_event_checked(root, mask, packed)

def is_connected(event_name, window, callback):
    member = '%sEvent' % event_name
    assert hasattr(xproto, member)

    key = (getattr(xproto, member), window)
    return key in __callbacks and callback in __callbacks[key]

def connect(event_name, window, callback):
    member = '%sEvent' % event_name
    assert hasattr(xproto, member)

    key = (getattr(xproto, member), window)
    __callbacks[key].append(callback)

def disconnect(event_name, window):
    member = '%sEvent' % event_name
    assert hasattr(xproto, member)

    key = (getattr(xproto, member), window)
    if key in __callbacks:
        del __callbacks[key]

def read(block=False):
    if block:
        e = conn.wait_for_event()
        __queue.appendleft(e)

    while True:
        e = conn.poll_for_event()

        if not e:
            break

        __queue.appendleft(e)

def main():
    try:
        while True:
            read(block=True)
            for e in queue():
                w = None
                if isinstance(e, xproto.MappingNotifyEvent):
                    w = None
                elif isinstance(e, xproto.MapRequestEvent):
                    # Force all MapRequestEvents to go to the root window so
                    # a window manager using xpybutil can get them.
                    w = root
                elif hasattr(e, 'window'):
                    w = e.window
                elif hasattr(e, 'event'):
                    w = e.event
                elif hasattr(e, 'owner'):
                    w = e.owner
                elif hasattr(e, 'requestor'):
                    w = e.requestor

                key = (e.__class__, w)
                for cb in __callbacks.get(key, []):
                    cb(e)
    except xcb_Exception:
        traceback.print_exc()
        sys.exit(1)

def queue():
    while len(__queue):
        yield __queue.pop()

def peek():
    return list(__queue)

