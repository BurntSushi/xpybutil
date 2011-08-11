import struct

import xcb.xproto

import event

__atom_cache = {}
__atom_nm_cache = {}

class Cookie(object):
    def __init__(self, cookie):
        self.cookie = cookie

    def check(self):
        return self.cookie.check()

class PropertyCookie(Cookie):
    def reply(self):
        return get_property_value(self.cookie.reply())

class PropertyCookieSingle(Cookie):
    def reply(self):
        ret = get_property_value(self.cookie.reply())

        if ret and isinstance(ret, list) and len(ret) == 1:
            return ret[0]
        return ret

class AtomCookie(Cookie):
    def reply(self):
        return self.cookie.reply().atom

class AtomNameCookie(Cookie):
    def reply(self):
        return str(self.cookie.reply().name.buf())

# Handle atom caching
def build_atom_cache(c, module):
    global __atom_cache, __atom_nm_cache

    for atom in module.__atoms:
        __atom_cache[atom] = get_atom_cookie(c, atom, only_if_exists=False)
    for atom in __atom_cache:
        if isinstance(__atom_cache[atom], AtomCookie):
            __atom_cache[atom] = __atom_cache[atom].reply()

    __atom_nm_cache = dict((v, k) for k, v in __atom_cache.iteritems())

def atom(atom_name):
    global __atom_cache

    if atom_name in __atom_cache:
        if isinstance(__atom_cache[atom_name], AtomCookie):
            __atom_cache[atom_name] = __atom_cache[atom_name].reply()
        return __atom_cache[atom_name]

    return None

def get_atom(c, atom_name, only_if_exists=False):
    global __atom_cache

    if atom_name in __atom_cache:
        if isinstance(__atom_cache[atom_name], AtomCookie):
            __atom_cache[atom_name] = __atom_cache[atom_name].reply()
    else:
        __atom_cache[atom_name] = get_atom_cookie(c, atom_name,
                                                  only_if_exists).reply()


    return __atom_cache[atom_name]

def get_atom_name(c, atom):
    global __atom_nm_cache

    if atom not in __atom_nm_cache:
        __atom_nm_cache[atom] = get_atom_name_cookie(c, atom).reply()

    return __atom_nm_cache[atom]

def get_atom_cookie(c, atom_name, only_if_exists=False):
    return AtomCookie(
                c.core.InternAtomUnchecked(only_if_exists, len(atom_name),
                                           atom_name))

def get_atom_name_cookie(c, atom):
    return AtomNameCookie(c.core.GetAtomNameUnchecked(atom))

def get_property(conn, window, atom):
    return conn.core.GetProperty(False, window, atom,
                                 xcb.xproto.GetPropertyType.Any, 0,
                                 2 ** 32 - 1)

def get_property_unchecked(conn, window, atom):
    return conn.core.GetPropertyUnchecked(False, window, atom,
                                 xcb.xproto.GetPropertyType.Any, 0,
                                 2 ** 32 - 1)

def get_property_value(property_reply):
    assert isinstance(property_reply, xcb.xproto.GetPropertyReply)

    if property_reply.format == 8:
        if 0 in property_reply.value:
            ret = []
            s = ''
            for o in property_reply.value:
                if o == 0:
                    ret.append(s)
                    s = ''
                else:
                    s += chr(o)
        else:
            ret = str(property_reply.value.buf())

        return ret
    elif property_reply.format in (16, 32):
        return list(struct.unpack('I' * property_reply.value_len,
                                  property_reply.value.buf()))

    return None

# I know this is bad... But i'm really not interested in
# developing for multiple screens...
def get_root(c):
    return c.get_setup().roots[0].root

def send_event(c, destination, event_mask, event, propagate=False):
    return c.core.SendEvent(propagate, destination, event_mask, event)

# Sends a client event to the root window
def _root_send_client_event_pack(window, message_type, data):
    # Pad the data
    data = data + ([0] * (5 - len(data)))

    # Taken from
    # http://xcb.freedesktop.org/manual/structxcb__client__message__event__t.html
    return struct.pack(
        'BBH7I',
        event.Event.ClientMessageEvent, # Event type
        32, # Format
        0, # Sequence
        window, # Window
        message_type, # Message type
        *data # Data
    )

def root_send_client_event(c, window, message_type, data):
    return c.core.SendEvent(False, get_root(c),
                                (xcb.xproto.EventMask.SubstructureNotify |
                                xcb.xproto.EventMask.SubstructureRedirect),
                            _root_send_client_event_pack(window, message_type,
                                                         data))

def root_send_client_event_checked(c, window, message_type, data):
    # I know this is bad... But i'm really not interested in
    # developing for multiple screens...
    root = c.get_setup().roots[0].root
    return c.core.SendEventChecked(
        False, root,
            (xcb.xproto.EventMask.SubstructureNotify |
            xcb.xproto.EventMask.SubstructureRedirect),
        _root_send_client_event_pack(window, message_type,
                                     data))
