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
import sys
import tarfile
import urllib.request
import zipfile

PYTHON = os.environ.get('PYTHON', None)
PYTHON_PYPY = os.environ.get('PYTHON_PYPY', None)
PYTHON_VERSION = os.environ.get('PYTHON_VERSION', None)
PYTHON_ARCH = os.environ.get('PYTHON_ARCH', None)


if not PYTHON_PYPY: sys.exit(0)
if os.path.exists(os.path.join(PYTHON, 'python.exe')): sys.exit(0)

URL = 'https://bitbucket.org/pypy/pypy/downloads/{}-{}-win32.zip'

url = URL.format(PYTHON_PYPY, PYTHON_VERSION)

response = urllib.request.urlopen(url)
with open('pypy.zip', 'wb') as pypy_zip:
    pypy_zip.write(response.read())

pypy_zip = zipfile.ZipFile('pypy.zip')
pypy_zip.extractall('C:\\')

os.rename('C:\\{}-{}-win32'.format(PYTHON_PYPY, PYTHON_VERSION), PYTHON)
try:
    os.unlink('C:\\pypy.zip')
except OSError:
    pass
os.link(os.path.join(PYTHON, 'pypy.exe'), os.path.join(PYTHON, 'python.exe'))

EZ_SETUP = 'https://bootstrap.pypa.io/ez_setup.py'

response = urllib.request.urlopen(EZ_SETUP)
with open(os.path.join(PYTHON, 'ez_setup.py'), 'wb') as get_pip:
    get_pip.write(response.read())

subprocess.call([os.path.join(PYTHON, 'python.exe'), os.path.join(PYTHON, 'ez_setup.py')])

PIP_URL = 'https://pypi.python.org/packages/source/p/pip/pip-7.1.2.tar.gz'

response = urllib.request.urlopen(PIP_URL)
with open(os.path.join('pip.tar.gz'), 'wb') as get_pip:
    get_pip.write(response.read())

pip_tar = tarfile.open('pip.tar.gz', 'r:gz')
pip_tar.extractall(PYTHON)

pip_setup = os.path.join(PYTHON, 'pip-7.1.2', 'setup.py')

subprocess.call([os.path.join(PYTHON, 'python.exe'), pip_setup, 'install'])