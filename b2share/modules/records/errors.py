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


import uuid

from jsonschema.exceptions import ValidationError
from jsonpatch import JsonPatchException
from jsonpointer import JsonPointerException

from invenio_rest.errors import RESTException, RESTValidationError, FieldError


class B2ShareRecordsError(RESTValidationError):
    """B2Share records error."""


class InvalidRecordError(B2ShareRecordsError):
    """Raise when a record is invalid."""


# TODO(edima): remove this when we have support for permissions
class AlteredRecordError(B2ShareRecordsError):
    """Raise when a record update changes what is considered
       immutable record data."""


class UnknownRecordType(B2ShareRecordsError):
    """Error raised when a record type cannot be determined.

    The two main record types are "published record" and "deposit".
    """

class AnonymousDepositSearch(B2ShareRecordsError):
    """Error raised when an anonymous user tries to search for drafts."""
    code = 401
    description = 'Only authenticated users can search for drafts.'


class InvalidOperationError(RESTException):
    """Raise when an invalid operation is performed on a record."""
    code = 400
    description = 'Invalid Operation.'


class GenericError(object):
    """Represents a generic error described by a simple message.

    .. note:: This is not an actual exception.
    """

    def __init__(self, message, code=None):
        """Init object.

        :param message: The text message to show.
        :param code: The HTTP status to return. (Default: ``None``)
        """
        self.res = dict(message=message)
        if code:
            self.res['code'] = code

    def to_dict(self):
        """Convert to dictionary.

        :returns: A dictionary message and, if initialized, the
            HTTP status code.
        """
        return self.res


def register_error_handlers(app):
    @app.errorhandler(ValidationError)
    def handle_validation_error(err):
        fieldpath = '/'.join([str(x) for x in err.path])
        message = err.message
        field = None
        if err.validator == 'required' or err.validator == 'additionalProperties':
            try:
                field = err.message.split('\'')[1]
                fieldpath = (fieldpath + '/' if fieldpath else '') + field
            except IndexError:
                pass # ignore
        if err.validator == 'required' and len(err.path) == 1 and \
                err.path[0] == 'community_specific' and is_valid_uuid(field):
            message = 'The "community_specific" metadata object must contain '\
                      'an object named "{}" containing the '\
                      'community-specific metadata fields'.format(field)
        return InvalidRecordError(errors=[
            FieldError(fieldpath, message)
        ])

    @app.errorhandler(JsonPointerException)
    def handle_validation_error(err):
        return InvalidOperationError(
            errors=[GenericError('Invalid JSON Pointer')]
        )


    @app.errorhandler(JsonPatchException)
    def handle_validation_error(err):
        return InvalidOperationError(
            errors=[GenericError('JSON-Patch error: {}'.format(err.args[0]))]
        )


def is_valid_uuid(argument):
    try:
        uuid.UUID(argument)
        return True
    except Exception:
        return False
