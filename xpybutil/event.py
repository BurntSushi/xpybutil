from collections import deque
import struct
import sys
import traceback

import xcb.xproto

import util

__queue = deque()
__callbacks = []

class Event:
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

def connect(event_name, window, callback):
    member = '%sEvent' % event_name
    assert hasattr(xcb.xproto, member)

    __callbacks.append((getattr(xcb.xproto, member), window, callback))

def disconnect(event_name, window):
    member = '%sEvent' % event_name
    assert hasattr(xcb.xproto, member)

    member = getattr(xcb.xproto, member)
    cbs = filter(lambda (et, win, cb): et == member and win == window,
                 __callbacks)
    for item in cbs:
        __callbacks.remove(item)

def send_event(c, destination, event_mask, event, propagate=False):
    return c.core.SendEvent(propagate, destination, event_mask, event)

def pack_client_message(window, message_type, *data):
    assert len(data) <= 5

    data = list(data)
    data += ([0] * (5 - len(data)))

    return struct.pack('BBH7I', Event.ClientMessageEvent, 32, 0, window,
                       message_type, *data)

def read(c, block=False):
    if block:
        e = c.wait_for_event()
        __queue.appendleft(e)

    while True:
        e = c.poll_for_event()

        if not e:
            break

        __queue.appendleft(e)

def event_loop(conn):
    try:
        while True:
            read(conn, block=True)
            for e in queue():
                w = None
                if hasattr(e, 'window'):
                    w = e.window
                elif hasattr(e, 'event'):
                    w = e.event
                elif hasattr(e, 'requestor'):
                    w = e.requestor

                for event_type, win, cb in __callbacks:
                    if win == w and isinstance(e, event_type):
                        cb(e)
    except xcb.Exception:
        traceback.print_exc()
        sys.exit(1)

def queue():
    while len(__queue):
        yield __queue.pop()

def peek():
    return list(__queue)

