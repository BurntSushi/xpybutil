#!/usr/bin/env python2

import argparse
import sys

from xpybutil.compat import xproto

import xpybutil
import xpybutil.event as event
import xpybutil.ewmh as ewmh
import xpybutil.keybind as keybind

epilog = '''
Using window-marker is exactly like using marks in vim. Namely, by pressing the
keybinding for "mark", window-marker then listens for one more letter (a-z) to
be entered. Whichever letter is entered will now be associated with the active
window.
If you now want to go back to that window (even if you're on a different
desktop), simply press the keybinding for "goto" and then enter the letter you
used to mark the window.
To set your own keybinding, please consult /usr/include/X11/keysymdef.h
and the output of `xmodmap`. The `xev` program may also be useful.
'''
parser = argparse.ArgumentParser(description='Vim-like marks for windows.',
                                 epilog=epilog)
parser.add_argument('-m', '--mark', default='Mod4-m', metavar='KEYBINDING',
                    help='keybinding to add a mark (default: %(default)s)')
parser.add_argument('-g', '--goto', default='Mod4-apostrophe',
                    metavar='KEYBINDING',
                    help='keybinding to goto a mark (default %(default)s)')
args = parser.parse_args()

keybinds = { args.mark: 'mark_window', args.goto: 'goto_window' }
keybindmap = {}
marked = {}
grabbing = None

def do_mark_window(letter):
    awin = ewmh.get_active_window().reply()
    if awin is not None:
        marked[letter] = awin

def do_goto_window(letter):
    if letter not in marked:
        print >> sys.stderr, 'mark %s does not exist' % letter
        return

    wid = marked[letter]
    try:
        wdesk = ewmh.get_wm_desktop(wid).reply()
        desktop = ewmh.get_current_desktop().reply()
        visibles = ewmh.get_visible_desktops().reply() or [desktop]

        if wdesk is not None and wdesk not in visibles:
            ewmh.request_current_desktop_checked(wdesk).check()
        ewmh.request_active_window_checked(wid, source=1).check()
    except xproto.BadWindow:
        print >> sys.stderr, '%d no longer exists' % wid

def mark_window():
    start_get_letter(do_mark_window)

def goto_window():
    start_get_letter(do_goto_window)

def start_get_letter(cb):
    global grabbing

    GS = xproto.GrabStatus
    if keybind.grab_keyboard(xpybutil.root).status == GS.Success:
        grabbing = cb

def cb_get_letter(e):
    global grabbing

    if grabbing is not None:
        keybind.ungrab_keyboard()
        sym = keybind.get_keysym(e.detail)
        letter = keybind.get_keysym_string(sym)

        if len(letter) == 1 and ord(letter) in range(ord('a'), ord('z') + 1):
            grabbing(letter.lower())

        grabbing = None

# This has to come first so it is called first in the event loop
event.connect('KeyPress', xpybutil.root, cb_get_letter)

for key_str, fun_str in keybinds.iteritems():
    if fun_str not in globals():
        print >> sys.stderr, 'No such function %s for %s' % (fun_str, key_str)
        continue

    fun = globals()[fun_str]
    if not keybind.bind_global_key('KeyPress', key_str, fun):
        print >> sys.stderr, 'Could not bind %s to %s' % (key_str, fun_str)

event.main()

