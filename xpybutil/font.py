"""
This module is pretty inadequate. Mostly because if you find
yourself wanting to use this module, you're probably doing something wrong.
(i.e., use pycairo or PIL.)

This module will likely be removed in the future.
"""
from xpybutil.compat import xproto

def get_font_height(qfont):
    return qfont.max_bounds.ascent + qfont.max_bounds.descent

def get_text_width(qfont, text):
    assert isinstance(qfont, xproto.QueryFontReply)

    return sum([qfont.char_infos[ord(i)].character_width for i in text])

def get_text_height(qfont, text):
    assert isinstance(qfont, xproto.QueryFontReply)

    cinfo = qfont.char_infos
    return max([cinfo[ord(i)].ascent + cinfo[ord(i)].descent for i in text])

