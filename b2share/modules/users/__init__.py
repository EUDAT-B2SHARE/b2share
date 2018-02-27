# -*- coding: utf-8 -*-
#
# This file is part of EUDAT B2Share.
# Copyright (C) 2016 University of Tuebingen, CERN.
# Copyright (C) 2015 University of Tuebingen.
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

"""B2SHARE module providing access to user accounts


B2SHARE is accessible to anonymous users (not authenticated). However some
actions can only be performed by authenticated users.

Invenio provides the ``invenio-accounts`` module which stores in the database
user account information.

The B2SHARE module ``b2share.modules.users`` adds some features on top of
``invenio-accounts``.

* A REST API enabling to read user information and to create **REST API Access
  Tokens**. See ``b2share.modules.users.views``.

* Permission classes limiting the access to the REST API. See the
  ``b2share.modules.users.permissions`` module.

REST API Access Tokens enable a user to send authenticated requests via the
REST API. Example: ``GET /api/user/?access_token=<ACCESS_TOKEN>``. See
``invenio-oauth2server`` for more information on Access Tokens.
"""

from __future__ import absolute_import, print_function

from .ext import B2ShareUsers

__all__ = ('B2ShareUsers')
