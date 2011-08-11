#==============================================================================
# PyTyle - An on-demand tiling manager
# Copyright (C) 2009-2010  Andrew Gallant <andrew@pytyle.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#==============================================================================

import sys

from distutils import sysconfig
from distutils.core import setup

try:
    import xcb.xproto, xcb.xcb, xcb.xinerama, xcb.randr
except:
    print ''
    print 'xpybutil requires the X Python Binding'
    print 'See: http://cgit.freedesktop.org/xcb/xpyb/'
    print 'Or xpyb-ng can be used. See', 'https://github.com/dequis/xpyb-ng'
    sys.exit(1)

setup(
    name = "xpybutil",
    author = "Andrew Gallant",
    author_email = "andrew@pytyle.com",
    version = "0.0.1",
    license = "GPL",
    description = "An incomplete xcb-util port plus some extras",
    long_description = "See README",
    url = "http://pytyle.com",
    platforms = 'POSIX',
    packages = ['xpybutil', 'xpybutil/keysymdef'],
    data_files = [('xpybutil', ['README'])]
)
