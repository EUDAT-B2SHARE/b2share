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

"""B2share records errors."""


from jsonschema.exceptions import ValidationError

from invenio_rest.errors import RESTValidationError, FieldError


class B2ShareRecordsError(RESTValidationError):
    """B2Share records error."""


class InvalidRecordError(B2ShareRecordsError):
    """Raise when a record has no community."""

# TODO(edima): remove this when we have support for permissions
class AlteredRecordError(B2ShareRecordsError):
    """Raise when a record update changes what is considered
       immutable record data."""


class EpicPIDError(Exception):
    """Raise when a record has no community."""


class UnknownRecordType(B2ShareRecordsError):
    """Error raised when a record type cannot be determined.

    The two main record types are "published record" and "deposit".
    """


def register_error_handlers(app):
    @app.errorhandler(ValidationError)
    def handle_validation_error(err):
        field = '/'.join(err.path)
        if err.validator == 'required' or err.validator == 'additionalProperties':
            try:
                field = err.message.split('\'')[1]
            except IndexError:
                pass # ignore
        return InvalidRecordError(errors=[
            FieldError(field, err.message)
        ])
