# -*- coding: utf-8 -*-
#
# Copyright (C) 2015, Maximilian Köhl <mail@koehlma.de>
#
# This program is free software: you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public License
# as published by the Free Software Foundation, either version 3 of
# the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from __future__ import print_function, unicode_literals, division

from collections import namedtuple

from uv.library import ffi, lib

from ..common import Enumeration
from ..error import UVError
from ..handle import HandleType
from .stream import Stream

WinSize = namedtuple('WinSize', ['width', 'height'])


def reset_mode():
    code = lib.uv_tty_reset_mode()
    if code < 0: raise UVError(code)


class TTYMode(Enumeration):
    NORMAL = lib.UV_TTY_MODE_NORMAL
    RAW = lib.UV_TTY_MODE_RAW
    IO = lib.UV_TTY_MODE_IO


@HandleType.TTY
class TTY(Stream):
    __slots__ = ['uv_tty']

    def __init__(self, fd, readable=False, loop=None):
        self.uv_tty = ffi.new('uv_tty_t*')
        super(TTY, self).__init__(self.uv_tty, loop)
        code = lib.cross_uv_tty_init(self.loop.uv_loop, self.uv_tty, fd, int(readable))
        if code < 0:
            self.destroy()
            raise UVError(code)

    @property
    def winsize(self):
        c_with, c_height = ffi.new('int*'), ffi.new('int*')
        code = lib.uv_tty_get_winsize(self.uv_tty, c_with, c_height)
        if code < 0: raise UVError(code)
        return WinSize(c_with[0], c_height[0])

    def set_mode(self, mode=TTYMode.NORMAL):
        code = lib.uv_tty_set_mode(self.uv_tty, mode)
        if code < 0: raise UVError(code)