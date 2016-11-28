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

"""B2share access permissions loader."""

from flask_login import current_user
from flask_principal import identity_loaded
from invenio_access.permissions import ParameterizedActionNeed
from flask import current_app
from werkzeug.local import LocalProxy
from flask_principal import AnonymousIdentity

from .permissions import AuthenticatedNeed


current_flask_security = LocalProxy(
    lambda: current_app.extensions['security']
)


def _load_permissions_on_identity_loaded(sender, identity):
    """Load the user permissions when his identity is loaded."""
    # if the user is not anonymous
    if current_user.get_id() is not None:
        # Set the identity user object
        identity.user = current_user
        # Add the need provided to authenticated users
        identity.provides.add(
            AuthenticatedNeed
        )

def _register_anonymous_loader():
    """Register the Anonymous Identity loader."""

    def anonymous_identity_loader():
        identity = AnonymousIdentity()
        # Here we can add configurable permissions to anonymous users.
        return identity
    current_flask_security.principal.identity_loader(anonymous_identity_loader)


def register_permissions_loader(app):
    """Register the permissions loader."""
    identity_loaded.connect_via(app)(_load_permissions_on_identity_loaded)
    app.before_first_request(_register_anonymous_loader)
