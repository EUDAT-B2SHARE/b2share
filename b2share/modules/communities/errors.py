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

"""B2Share Communities exceptions."""

from __future__ import absolute_import

from invenio_rest.errors import RESTException


class InvalidCommunityError(Exception):
    """Exception raised when a community is invalid."""
    pass


class CommunityDoesNotExistError(Exception):
    """Exception raised when a requested community does not exist."""
    pass


class CommunityDeletedError(Exception):
    """Exception raised when a requested community is marked as deleted."""
    pass


class InvalidPublicationStateError(RESTException):
    """Exception raised when a deposit is an invalid publication state."""

    code = 400
    """HTTP Status code."""


class NotACommunityRoleError(RESTException):
    """Exception raised a role does not belong to a community."""

    code = 400
    description = 'This role doesn\'t belong to any community.'
