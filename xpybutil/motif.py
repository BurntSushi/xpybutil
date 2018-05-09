"""
Implements a subset of the Motif spec. This module exists
because some window managers still use this as the only way of
toggling window decorations via events.
"""
import struct

from xpybutil.compat import xproto

from xpybutil import conn as c
from xpybutil import util

__atoms = ['_MOTIF_WM_HINTS']

class Hint:
    Functions = 1 << 0
    Decorations = 1 << 1
    InputMode = 1 << 2
    Status = 1 << 3

class Function:
    _None = 0
    All = 1 << 0
    Resize = 1 << 1
    Move = 1 << 2
    Minimize = 1 << 3
    Maximize = 1 << 4
    Close = 1 << 5

class Decoration:
    _None = 0
    All = 1 << 0
    Border = 1 << 1
    ResizeH = 1 << 2
    Title = 1 << 3
    Menu = 1 << 4
    Minimize = 1 << 5
    Maximize = 1 << 6

class Input:
    Modeless = 0
    PrimaryApplicationModal = 1
    SystemModal = 2
    FullApplicationModal = 3

class Status:
    TearoffWindow = 1 << 0

# Some aliases
atom = util.get_atom
preplace = xproto.PropMode.Replace

# Build the atom cache for quicker access
util.build_atom_cache(__atoms)

# _MOTIF_WM_HINTS

class MotifHintsCookie(util.PropertyCookie):
    def reply(self):
        v = util.PropertyCookie.reply(self)

        if not v:
            return None

        return {
            'flags': {
                'Functions': v[0] & Hint.Functions > 0,
                'Decorations': v[0] & Hint.Decorations > 0,
                'InputMode': v[0] & Hint.InputMode > 0,
                'Status': v[0] & Hint.Status > 0
            },
            'function': v[1],
            'decoration': v[2],
            'input': v[3],
            'status': v[4]
        }

def get_hints(window):
    return MotifHintsCookie(util.get_property(window, '_MOTIF_WM_HINTS'))

def get_hints_unchecked(window):
    cook = util.get_property_unchecked(window, '_MOTIF_WM_HINTS')
    return MotifHintsCookie(cook)

def _pack_hints(flags, function, decoration, input, status):
    hints = [0] * 5

    if flags & Hint.Functions:
        hints[1] = function

    if flags & Hint.Decorations:
        hints[2] = decoration

    if flags & Hint.InputMode:
        hints[3] = input

    if flags & Hint.Status:
        hints[4] = status

    hints[0] = flags

    return struct.pack('I' * 5, *hints)

def set_hints(window, flags, function=Function._None,
              decoration=Decoration._None, input=Input.Modeless,
              status=Status.TearoffWindow):
    packed = _pack_hints(flags, function, decoration, input, status)
    return c.core.ChangeProperty(preplace, window, atom('_MOTIF_WM_HINTS'),
                                 atom('_MOTIF_WM_HINTS'), 32, 5, packed)

def set_hints_checked(window, flags, function=Function._None,
                      decoration=Decoration._None, input=Input.Modeless,
                      status=Status.TearoffWindow):
    packed = _pack_hints(flags, function, decoration, input, status)
    return c.core.ChangePropertyChecked(preplace, window,
                                        atom('_MOTIF_WM_HINTS'),
                                        atom('_MOTIF_WM_HINTS'), 32, 5, packed)

