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

"""B2Share Schemas exceptions."""

from __future__ import absolute_import

from doschema.errors import JSONSchemaCompatibilityError
from invenio_rest.errors import FieldError, RESTException


class B2ShareSchemasError(RESTException):
    """Base class for the B2Share Schemas module."""

    def __init__(self, description=None):
        """Constructor"""
        super(B2ShareSchemasError, self).__init__()
        if description is not None:
            self.description = description

#
# JSON SCHEMA ERRORS
#

class InvalidJSONSchemaError(B2ShareSchemasError):
    """Exception raised when a JSON Schema is considered as invalid."""
    code = 400


class MissingRequiredFieldSchemaError(B2ShareSchemasError):
    """Exception raised when a JSON Schema requires one or more fields that are not defined."""
    code = 400

class MissingPresentationFieldSchemaError(B2ShareSchemasError):
    """Exception raised when a JSON Schema presentation definition requires one or more fields that are not defined."""
    code = 400

#
# ROOT SCHEMA ERRORS
#

class RootSchemaDoesNotExistError(B2ShareSchemasError):
    """Exception raised when a requested root schema does not exist."""
    code = 404


class RootSchemaAlreadyExistsError(B2ShareSchemasError):
    """A new root schema conflicts with an existing one."""
    code = 400


class InvalidRootSchemaError(B2ShareSchemasError):
    """Exception raised when a root schema is invalid."""
    code = 400


#
# BLOCK SCHEMA ERRORS
#

class InvalidBlockSchemaError(B2ShareSchemasError):
    """Exception raised when a block schema is invalid."""
    code = 400


class BlockSchemaDoesNotExistError(B2ShareSchemasError):
    """Exception raised when a requested block schema does not exist."""
    code = 404


class BlockSchemaIsDeprecated(B2ShareSchemasError):
    """Exception raised while trying to add a new version to a deprecated block schema."""  # noqa
    code = 400


class BlockSchemaVersionIsReleased(B2ShareSchemasError):
    """Exception raised while trying to modify a released block schema."""
    code = 400


#
# BLOCK SCHEMA VERSION ERRORS
#

class InvalidSchemaVersionError(B2ShareSchemasError):
    """Exception raised when trying to add a version with wrong id."""

    MESSAGE = """Version number is invalid. Provided version number should
                follow the last existing version number, which currently
                is {0}."""
    code = 400

    def __init__(self, last_version):
        """Constructor."""
        self.last_version = last_version
        """Error message."""
        super(InvalidSchemaVersionError, self).__init__(
            self.MESSAGE.format(last_version)
        )


class SchemaVersionExistsError(B2ShareSchemasError):
    """Exception raised when trying to add an existing version."""

    MESSAGE = """Version number already exists. Provided version number should
                follow the last existing version number, which currently
                is {0}."""
    code = 400

    def __init__(self, last_version):
        """Constructor."""
        self.last_version = last_version
        """Error message."""
        super(SchemaVersionExistsError, self).__init__(
            self.MESSAGE.format(last_version)
        )

#
# COMMUNITY SCHEMA VERSION ERRORS
#


class CommunitySchemaIsImmutable(B2ShareSchemasError):
    """Exception raised when a released Community schema is edited."""
    code = 400


class CommunitySchemaDoesNotExistError(B2ShareSchemasError):
    """Exception raised when a requested Community schema does not exist."""
    code = 404


#
# Backward Incompatible JSON Schema.
#

class BackwardIncompatibleJSONSchemaError(B2ShareSchemasError):
    """Exception raised when a JSON Schema is backward incompatible."""
    code = 400


def register_error_handlers(app):
    @app.errorhandler(JSONSchemaCompatibilityError)
    def handle_schema_compatibility_error(err):
        return BackwardIncompatibleJSONSchemaError(str(err)).get_response()
