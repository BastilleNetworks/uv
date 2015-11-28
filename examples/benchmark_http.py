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

import uv

RESPONSE = (b'HTTP/1.1 200 OK\r\n'
            b'Content-Type: text/plain\r\n'
            b'Content-Length: 13\r\n\r\n'
            b'Hello World!\n')


def on_shutdown(request, _):
    request.handle.close()


def on_read(stream, length, data):
    if not data or length < 0: stream.close()
    data = data.strip()
    if not data: return
    stream.write(RESPONSE)
    stream.shutdown(on_shutdown)


def on_connection(server, _):
    connection = server.accept()
    connection.read_start(callback=on_read)


def on_quit(*_):
    uv.close_all_handles()


def main():
    loop = uv.Loop.current_loop()

    server = uv.TCP()
    server.bind('0.0.0.0', 4444)
    server.listen(20, callback=on_connection)

    sigint = uv.Signal()
    sigint.start(uv.Signals.SIGINT, callback=on_quit)

    loop.run()


if __name__ == '__main__':
    main()