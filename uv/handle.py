# -*- coding: utf-8 -*-
#
# Copyright (C) 2015, Maximilian Köhl <mail@koehlma.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import enum

from .library import ffi, lib, attach, detach, dummy_callback, is_linux

from .error import UVError, ClosedStructure
from .loop import Loop

__all__ = ['close_all_handles', 'Handle']

handles = set()


def close_all_handles(callback=None):
    for handle in handles: handle.close(callback)


class HandleType(enum.IntEnum):
    UNKNOWN = lib.UV_UNKNOWN_HANDLE
    HANDLE = lib.UV_HANDLE
    ASYNC = lib.UV_ASYNC
    CHECK = lib.UV_CHECK
    FILE = lib.UV_FILE
    IDLE = lib.UV_IDLE
    PIPE = lib.UV_NAMED_PIPE
    POLL = lib.UV_POLL
    PREPARE = lib.UV_PREPARE
    PROCESS = lib.UV_PROCESS
    SIGNAL = lib.UV_SIGNAL
    STREAM = lib.UV_STREAM
    TCP = lib.UV_TCP
    TIMER = lib.UV_TIMER
    TTY = lib.UV_TTY
    UDP = lib.UV_UDP

    FS_EVENT = lib.UV_FS_EVENT
    FS_POLL = lib.UV_FS_POLL

    def __call__(self, cls):
        self.cls = cls
        return cls


@ffi.callback('uv_close_cb')
def uv_close_cb(uv_handle):
    handle = detach(uv_handle)
    with handle.loop.callback_context:
        handle.on_closed(handle)
    handle.destroy()


@HandleType.UNKNOWN
@HandleType.HANDLE
class Handle(object):
    __slots__ = ['uv_handle', 'c_attachment', 'loop', 'destroyed', 'on_closed']

    def __init__(self, uv_handle, loop=None):
        self.uv_handle = ffi.cast('uv_handle_t*', uv_handle)
        self.c_attachment = attach(self.uv_handle, self)
        self.on_closed = dummy_callback
        self.loop = loop or Loop.current_loop()
        if self.loop.closed: raise ClosedStructure()
        self.destroyed = False
        handles.add(self)

    @property
    def active(self):
        if self.destroyed: return False
        return bool(lib.uv_is_active(self.uv_handle))

    @property
    def closed(self):
        if self.destroyed: return True
        return bool(lib.uv_is_closing(self.uv_handle))

    @property
    def referenced(self):
        if self.destroyed: return False
        return bool(lib.uv_has_ref(self.uv_handle))

    @property
    def send_buffer_size(self):
        c_buffer_size = ffi.new('int*')
        code = lib.uv_send_buffer_size(self.uv_handle, c_buffer_size)
        if code < 0: raise UVError(code)
        return c_buffer_size[0]

    @send_buffer_size.setter
    def send_buffer_size(self, value):
        c_buffer_size = ffi.new('int*', int(value / 2) if is_linux else value)
        code = lib.uv_send_buffer_size(self.uv_handle, c_buffer_size)
        if code < 0: raise UVError(code)

    @property
    def receive_buffer_size(self):
        """
        Gets the size of the receive buffer that the operating system uses for
        the socket. The following handles are supported: TCP and UDP handles on
        Unix and Windows, Pipe handles only on Unix.

        .. note::

            Unlike libuv this library abstracts the different behaviour on Linux
            and other operating system.

        :return: size of the receive buffer
        :rtype: int
        """
        c_buffer_size = ffi.new('int*')
        code = lib.uv_recv_buffer_size(self.uv_handle, c_buffer_size)
        if code < 0: raise UVError(code)
        return c_buffer_size[0]

    @receive_buffer_size.setter
    def receive_buffer_size(self, value):
        """
        :param value:  size of the receive buffer
        :type value: int
        :return:
        """
        if self.destroyed: raise ClosedStructure()
        c_buffer_size = ffi.new('int*', int(value / 2) if is_linux else value)
        code = lib.uv_recv_buffer_size(self.uv_handle, c_buffer_size)
        if code < 0: raise UVError(code)

    def fileno(self):
        """
        Gets the platform dependent file descriptor equivalent. The following
        handles are supported: TCP, UDP, TTY, Pipes and Poll. On all other
        handles this will raise :class:`uv.UVError` with `StatusCode.EINVAL`.

        :raises uv.UVError: error during receiving fileno
        :return: platform dependent file descriptor equivalent
        :rtype: int
        """
        if self.destroyed: raise ClosedStructure()
        uv_fd = ffi.new('uv_os_fd_t*')
        code = lib.uv_fileno(self.uv_handle, uv_fd)
        if code < 0: raise UVError(code)
        return ffi.cast('int*', uv_fd)[0]

    def reference(self):
        """
        References the handle. If the event loop runs in default mode it will
        exit when there are no more active and referenced handles left. This
        has nothing to do with CPython's reference counting.
        """
        if self.destroyed: raise ClosedStructure()
        lib.uv_ref(self.uv_handle)

    def dereference(self):
        """
        Dereferences the handle. If the event loop runs in default mode it will
        exit when there are no more active and referenced handles left. This has
        nothing to do with CPython's reference counting.
        """
        if self.destroyed: raise ClosedStructure()
        lib.uv_unref(self.uv_handle)

    def close(self, on_closed=None):
        """
        Closes the handle and frees all resources afterwards. Please make sure
        to call this method on any handle you do not need anymore. Handles do
        not close automatically and are also not garbage collected unless you
        have closed them exlicitly (explicit is better than implicit).

        :param on_closed: callback called after the handle has been closed
        :type on_closed: (Handle) -> None
        """
        if self.destroyed: return
        self.on_closed = on_closed or self.on_closed
        lib.uv_close(self.uv_handle, uv_close_cb)

    def destroy(self):
        """
        .. warning::

            This method is used internally to free all allocated C resources and
            make sure there are no references from Python anymore to those objects
            after the handle has been closed. You should never call this directly!
        """
        self.uv_handle = None
        handles.remove(self)
        self.destroyed = True
