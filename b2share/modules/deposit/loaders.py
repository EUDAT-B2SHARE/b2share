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
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""B2Share deposit input loaders."""

from flask import abort, request
from invenio_rest.errors import RESTValidationError, FieldError

IMMUTABLE_PATHS= {
    # fields added by the serializer
    '/owners'
    '/ePIC_PID'
    '/DOI',
    '/files',
    # real fields
    '/community',
    '/$schema',
    '/_pid',
    '/_oai',
    '/_files',
    '/_deposit',
}


def patch_input_loader(record=None):
    data = request.get_json(force=True)
    if data is None:
        abort(400)
    modified_fields = {cmd['path'] for cmd in data
                       if 'path' in cmd and 'op' in cmd and cmd['op'] != 'test'}
    errors = [FieldError(field, 'The field "{}" is immutable.'.format(field))
              for field in IMMUTABLE_PATHS.intersection(modified_fields)]
    if len(errors) > 0:
        raise RESTValidationError(errors=errors)
    return data
