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

"""Community models."""

import uuid
from itertools import chain

from invenio_db import db
from sqlalchemy.sql import expression
from sqlalchemy_utils.models import Timestamp
from sqlalchemy_utils.types import UUIDType
from sqlalchemy import event
from invenio_accounts.models import Role
from invenio_access.models import ActionRoles


class Community(db.Model, Timestamp):
    """Represent a community metadata inside the SQL database.
    Additionally it contains two columns ``created`` and ``updated``
    with automatically managed timestamps.
    """

    __tablename__ = 'b2share_community'

    id = db.Column(
        UUIDType,
        primary_key=True,
        default=uuid.uuid4,
    )
    """Community identifier."""  # noqa

    # community name
    name = db.Column(
        db.String(80), unique=True, nullable=False)

    # community description
    description = db.Column(
        db.String(2000), nullable=False)

    # link to the logo
    logo = db.Column(
        db.String(300), nullable=True)

    # Flag marking the community as deleted
    deleted = db.Column(db.Boolean, nullable=False,
                        server_default=expression.false())

    # Publication workflow used in this community
    publication_workflow = db.Column(db.String(80), nullable=False,
                                     default='review_and_publish')

    # Restrict record creation
    restricted_submission = db.Column(db.Boolean, nullable=False,
                                      server_default=expression.false(),
                                      default=False)


def _communiy_admin_role_name(community):
    """Generate the name of the given community's admin role."""
    return 'com:{0}:{1}'.format(community.id.hex, 'admin')


def _communiy_member_role_name(community):
    """Generate the name of the given community's member role."""
    return 'com:{0}:{1}'.format(community.id.hex, 'member')


@event.listens_for(Community, 'after_insert')
def receive_before_insert(mapper, connection, target):
    """Create community admin and member roles and add their permissions."""
    from b2share.modules.deposit.permissions import (
        create_deposit_need_factory, read_deposit_need_factory,
        update_deposit_metadata_need_factory,
        update_deposit_publication_state_need_factory,
    )
    from b2share.modules.deposit.api import PublicationStates

    admin_role = Role(
        name=_communiy_admin_role_name(target),
        description='Admin role of the community "{}"'.format(target.name)
    )
    member_role = Role(
        name=_communiy_member_role_name(target),
        description='Member role of the community "{}"'.format(target.name)
    )

    db.session.add(admin_role)
    db.session.add(member_role)
    member_needs = [
        create_deposit_need_factory(str(target.id)),
    ]
    admin_needs = [
        read_deposit_need_factory(
            community=str(target.id),
            publication_state=PublicationStates.submitted.name
        ),
        read_deposit_need_factory(
            community=str(target.id),
            publication_state=PublicationStates.published.name
        ),
        update_deposit_metadata_need_factory(
            community=str(target.id),
            publication_state=PublicationStates.submitted.name
        ),
        # permission to publish a submission
        update_deposit_publication_state_need_factory(
            community=str(target.id),
            old_state=PublicationStates.submitted.name,
            new_state=PublicationStates.published.name
        ),
        # permission to ask the owners to fix a submission before resubmitting
        update_deposit_publication_state_need_factory(
            community=str(target.id),
            old_state=PublicationStates.submitted.name,
            new_state=PublicationStates.draft.name
        )
    ]
    for need in member_needs:
        db.session.add(ActionRoles.allow(need, role=member_role))
    for need in chain (member_needs, admin_needs):
        db.session.add(ActionRoles.allow(need, role=admin_role))


__all__ = (
    'Community',
    'CommunityRole',
)
