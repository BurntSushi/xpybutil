import struct

import xcb.xproto

from xpybutil import conn, root

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
def build_atom_cache(atoms):
    global __atom_cache, __atom_nm_cache

    for atom in atoms:
        __atom_cache[atom] = get_atom_cookie(atom, only_if_exists=False)
    for atom in __atom_cache:
        if isinstance(__atom_cache[atom], AtomCookie):
            __atom_cache[atom] = __atom_cache[atom].reply()

    __atom_nm_cache = dict((v, k) for k, v in __atom_cache.iteritems())

def get_atom(atom_name, only_if_exists=False):
    global __atom_cache

    a = __atom_cache.setdefault(atom_name,
                                get_atom_cookie(atom_name, 
                                                only_if_exists).reply())
    if isinstance(a, AtomCookie):
        a = a.reply()

    return a

def get_atom_name(atom):
    global __atom_nm_cache

    a = __atom_nm_cache.setdefault(atom, get_atom_name_cookie(atom).reply())

    if isinstance(a, AtomNameCookie):
        a = a.reply()
    
    return a

def get_atom_cookie(atom_name, only_if_exists=False):
    atom = conn.core.InternAtomUnchecked(only_if_exists, len(atom_name),
                                         atom_name)
    return AtomCookie(atom)

def get_atom_name_cookie(atom):
    return AtomNameCookie(conn.core.GetAtomNameUnchecked(atom))

def get_property(window, atom):
    if isinstance(atom, basestring):
        atom = get_atom(atom)
    return conn.core.GetProperty(False, window, atom,
                                 xcb.xproto.GetPropertyType.Any, 0,
                                 2 ** 32 - 1)

def get_property_unchecked(window, atom):
    if isinstance(atom, basestring):
        atom = get_atom(atom)
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

def get_parent_window(window):
    return conn.core.QueryTree(window).reply().parent

