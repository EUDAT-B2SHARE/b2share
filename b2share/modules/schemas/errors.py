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


class B2ShareSchemasError(Exception):
    """Base class for the B2Share Schemas module."""
    pass


#
# JSON SCHEMA ERRORS
#

class InvalidJSONSchemaError(B2ShareSchemasError):
    """Exception raised when a JSON Schema is considered as invalid."""
    pass


#
# ROOT SCHEMA ERRORS
#

class RootSchemaDoesNotExistError(B2ShareSchemasError):
    """Exception raised when a requested root schema does not exist."""
    pass


class InvalidRootSchemaError(B2ShareSchemasError):
    """Exception raised when a root schema is invalid."""
    pass


#
# BLOCK SCHEMA ERRORS
#

class InvalidBlockSchemaError(B2ShareSchemasError):
    """Exception raised when a block schema is invalid."""
    pass


class BlockSchemaDoesNotExistError(B2ShareSchemasError):
    """Exception raised when a requested block schema does not exist."""
    pass


class BlockSchemaIsDeprecated(B2ShareSchemasError):
    """Exception raised while trying to add a new version to a deprecated block schema."""  # noqa
    pass


class BlockSchemaVersionIsReleased(B2ShareSchemasError):
    """Exception raised while trying to modify a released block schema."""
    pass

#
# COMMUNITY SCHEMA VERSION ERRORS
#


class CommunitySchemaIsImmutable(B2ShareSchemasError):
    """Exception raised when a released Community schema is edited."""
    pass


class CommunitySchemaDoesNotExistError(B2ShareSchemasError):
    """Exception raised when a requested Community schema does not exist."""
    pass
