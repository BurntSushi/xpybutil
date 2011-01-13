from collections import deque
import struct

import xcb.xproto

import util

__queue = deque()

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

def queue():
    while len(__queue):
        yield __queue.pop()

def peek():
    return list(__queue)