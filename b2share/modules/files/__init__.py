# -*- coding: utf-8 -*-
#
# This file is part of EUDAT B2Share.
# Copyright (C) 2016 CERN.
#
# B2Share is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# B2Share is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with B2Share; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""B2Share files module.

The files module provides the storage class for files with external PIDs
and background tasks for file checksum verification.

The storage class B2ShareFileStorage is assigned to files with external PIDs
in order to change the procedure when downloading and
redirect to the PID instead of starting a file download.

The API for interacting with files is provided directly by invenio-files-rest.

The permissions in the files REST API dictate that files cannot be changed
if their record is published.
Also, the files of a draft can only be modified by the creator of the draft
or the community administrator.
"""

from __future__ import absolute_import, print_function

from .ext import B2ShareFiles

__all__ = ('B2ShareFiles')
