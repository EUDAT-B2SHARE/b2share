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

"""B2Share Deposit errors."""


import json
from invenio_rest.errors import RESTValidationError, FieldError


class B2ShareDepositError(RESTValidationError):
    """B2Share Deposit module Exception."""


class InvalidDepositError(B2ShareDepositError):
    """Exception raised when the Deposit is invalid."""


class VersioningDepositError(B2ShareDepositError):
    """Versioning related exception."""


class DraftExistsVersioningError(VersioningDepositError):
    """Exception raised when trying to create a new version of a record which
    already is associated with a new version draft."""
    description = ("Versioning error. A draft already exists in the "+
                   "version chain designated by the specified `version_of` "+
                   "parameter.")

    def __init__(self, draft_pid):
        super(DraftExistsVersioningError, self).__init__()
        self.draft_pid = draft_pid

    def get_body(self, environ=None):
        body = dict(
            status=self.code,
            message=self.get_description(environ),
            goto_draft=self.draft_pid.pid_value,
        )
        return json.dumps(body)

class IncorrectRecordVersioningError(VersioningDepositError):
    """Exception raised when trying to create a new version of a record which
    is not the latest in a versioning chain or is the parent pid."""
    description = ("Versioning error. The `version_of` parameter " +
                  "must specify the id of the latest published record in a "+
                  "version chain.")

    def __init__(self, record_pid_value):
        super(IncorrectRecordVersioningError, self).__init__()
        self.record_pid_value = record_pid_value

    def get_body(self, environ=None):
        body = dict(
            status=self.code,
            message=self.get_description(environ),
            use_record=self.record_pid_value,
        )
        return json.dumps(body)

class RecordNotFoundVersioningError(VersioningDepositError):
    """Exception raised when the `version_of` parameter does not point to
    a record."""
    description = ("Versioning error. The `version_of` parameter " +
                  "must point to a valid published record.")
