# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2017 CERN.
#
# Invenio is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""REST API request input loaders."""

import json

from flask import request
from jsonpatch import JsonPatchException, JsonPointerException, apply_patch
from invenio_accounts_rest.errors import PatchJSONFailureRESTError
from invenio_rest.errors import FieldError, RESTValidationError


def account_json_loader(**kwargs):
    """Accounts REST API data loader for JSON input."""
    data = request.get_json(force=True)
    for key in data:
        # only "active" field is immutable
        if key != 'active':
            raise RESTValidationError(errors=[
                FieldError(key, 'Field {} is immutable'.format(key))
            ])
    return data


def account_json_patch_loader(user=None, **kwargs):
    """Accounts REST API data loader for JSON Patch input."""
    data = request.get_json(force=True)
    if data is None:
        abort(400)
    modified_fields = {
        cmd['path'][1:] for cmd in data
        if 'path' in cmd and 'op' in cmd and cmd['op'] != 'test'
    }
    errors = [
        FieldError(field, 'Unknown or immutable field {}.'.format(field))
        # only "active" field is immutable
        for field in modified_fields if field != 'active'
    ]
    if len(errors) > 0:
        raise RESTValidationError(errors=errors)

    original = {
        'active': user.active
    }
    try:
        patched = apply_patch(original, data)
    except (JsonPatchException, JsonPointerException):
        raise PatchJSONFailureRESTError()
    return patched
