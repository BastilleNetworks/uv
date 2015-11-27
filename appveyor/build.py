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

import os
import subprocess

PYTHON_PYPY = os.environ.get('PYTHON_PYPY', None)

subprocess.call(['python', 'setup.py', 'bdist_wheel'])
subprocess.call(['python', 'setup.py', 'bdist_wininst'])

if not PYTHON_PYPY:
    subprocess.call(['python', 'setup.py', 'bdist_msi'])