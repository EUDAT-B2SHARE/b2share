# -*- coding: utf-8 -*-
#
# This file is part of EUDAT B2Share.
# Copyright (C) 2016 University of Tuebingen, CERN
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
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""Communities interface and API."""

from __future__ import absolute_import

import uuid

from invenio_db import db
from jsonpatch import apply_patch

import sqlalchemy
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import StatementError

from invenio_accounts.models import Role

from .errors import CommunityDeletedError, CommunityDoesNotExistError, \
    InvalidCommunityError

from .signals import after_community_delete, after_community_insert, \
    after_community_update, before_community_delete, before_community_insert, \
    before_community_update

from .models import Community as CommunityMetadata, _community_admin_role_name, \
    _community_member_role_name


class Community(object):
    """B2Share Community."""

    def __init__(self, model):
        """
        Args:
            model (:class:`b2share.modules.communities.models.Community`):
                database community model.
        """
        self.model = model

    @classmethod
    def get(cls, id=None, name=None, with_deleted=False):
        """Retrieve a community by its id or name.

        Args:
            id (str): id of the :class:`CommunityInterface` instance.
            name (str): name of the :class:`CommunityInterface instance.
            with_deleted (bool): enable the retrieval of deleted records.

        Returns:
            :class:`CommunityInterface`: The requested community.

        Raises:
            b2share.modules.communities.errors.CommunityDoesNotExistError: The
                requested community was not found.
            b2share.modules.communities.errors.CommunityDeletedError: The
                requested community is marked as deleted and `with_deleted` is
                    False.
            ValueError: :attr:`id` and :attr:`name` are not set or both are
                    set.
        """
        if not id and not name:
            raise ValueError('"id" or "name" should be set.')
        if id and name:
            raise ValueError('"id" and "name" should not be both set.')
        try:
            if id:
                metadata = CommunityMetadata.query.filter(
                    CommunityMetadata.id == id).one()
            else:
                metadata = CommunityMetadata.query.filter(
                    CommunityMetadata.name == name).one()
            if metadata.deleted and not with_deleted:
                raise CommunityDeletedError(id)
            return cls(metadata)
        except (NoResultFound, StatementError) as e:
            raise CommunityDoesNotExistError(id) from e

    @classmethod
    def get_all(cls, start=None, stop=None, name=None):
        """Searches for matching communities."""
        if (start is None and stop is None):
            if name is None:
                metadata = CommunityMetadata.query.order_by(CommunityMetadata.name)
            else:
                metadata = CommunityMetadata.query.filter(
                    CommunityMetadata.name.like(name)
                    ).order_by(CommunityMetadata.name)
        elif start is not None and stop is not None:
            if name is None:
                metadata = CommunityMetadata.query.order_by(
                    CommunityMetadata.name).limit(stop)[start:]
            else:
                metadata = CommunityMetadata.query.filter(
                    CommunityMetadata.name.like(name)
                ).order_by(CommunityMetadata.name).limit(stop)[start:]
        else:
            # one of them is None this cannot happen
            raise ValueError("Neither or both start and stop should be None")
        return [cls(md) for md in metadata]

    @classmethod
    def create_community(cls, name, description, logo=None, id_=None,
                         publication_workflow=None,
                         restricted_submission=False):
        """Create a new Community.

        A new community is implicitly associated with a new, empty, schema
        list.

        Args:
            name (str): Community name.
            description (str): Community description.
            logo (str): URL to the Community logo.

        Returns:
            :class:`CommunityInterface`: the newly created community.

        Raises:
            b2share.modules.communities.errors.InvalidCommunityError: The
                community creation failed because the arguments are not valid.
        """
        try:
            with db.session.begin_nested():

                kwargs = {
                    'name': name,
                    'description': description,
                    'logo': logo,
                    'publication_workflow': publication_workflow,
                    'restricted_submission': restricted_submission
                }

                if id_ is not None:
                    kwargs['id'] = id_
                model = CommunityMetadata(**kwargs)
                community = cls(model)
                before_community_insert.send(community)
                db.session.add(model)
        except sqlalchemy.exc.IntegrityError as e:
            raise InvalidCommunityError() from e
        after_community_insert.send(community)
        return community

    def update(self, data, clear_fields=False):
        """Update multiple fields of the community at the same time.

        If the update fails, none of the community's fields are modified.

        Args:
            data (dict): can have one of those fields: name, description, logo.
                it replaces the given values.
            clear_fields (bool): if True, set not specified fields to their
                default value.

        Returns:
            :class:`Community`: self

        Raises:
            b2share.modules.communities.errors.InvalidCommunityError: The
                community update failed because the resulting community is
                not valid.
        """
        try:
            with db.session.begin_nested():
                before_community_update.send(self)
                if clear_fields:
                    for field in ['name', 'description', 'logo']:
                        setattr(self.model, field, data.get(field, None))
                        self.model.publication_workflow = \
                            'review_and_publish'
                        self.model.restricted_submission = False
                # FIXME: what do we do when the publication_workflow is changed?
                # Do we run the new workflow on all records in order to fix the
                # their publication_state?
                for key, value in data.items():
                    setattr(self.model, key, value)
                db.session.merge(self.model)
        except sqlalchemy.exc.IntegrityError as e:
            raise InvalidCommunityError() from e
        after_community_update.send(self)
        return self

    def patch(self, patch):
        """Update the community's metadata with a json-patch.

        Args:
            patch (dict): json-patch which can modify the following fields:
                name, description, logo.

        Returns:
            :class:`Community`: self

        Raises:
            jsonpatch.JsonPatchConflict: the json patch conflicts on the
                community.

            jsonpatch.InvalidJsonPatch: the json patch is invalid.

            b2share.modules.communities.errors.InvalidCommunityError: The
                community patch failed because the resulting community is
                not valid.
        """
        data = apply_patch({
            'name': self.model.name,
            'description': self.model.description,
            'logo': self.model.logo,
            'publication_workflow': self.model.publication_workflow,
            'restricted_submission': self.model.restricted_submission,
        }, patch, True)
        self.update(data)
        return self

    # TODO: add properties for getting schemas and admins

    def delete(self):
        """Mark a community as deleted.

        Returns:
            :class:`Community`: self
        """
        with db.session.begin_nested():
            before_community_delete.send(self)
            self.model.deleted = True
            db.session.merge(self.model)
            # FIXME: What do we do with this community's records?
        after_community_delete.send(self)
        return self

    @property
    def id(self):
        """Get community id."""
        return self.model.id

    @property
    def created(self):
        """Get creation timestamp."""
        return self.model.created

    @property
    def updated(self):
        """Get last updated timestamp."""
        return self.model.updated

    @property
    def deleted(self):
        """Get community deletion state.

        Returns:
            date: True if the community is deleted, else False.
        """
        return self.model.deleted

    @property
    def name(self):
        """Retrieve community's name."""
        return self.model.name

    @property
    def description(self):
        """Retrieve community's description."""
        return self.model.description

    @property
    def logo(self):
        """Retrieve community's logo."""
        return self.model.logo

    @property
    def publication_workflow(self):
        """Retrieve the name of the publication workflow."""
        return self.model.publication_workflow

    @property
    def restricted_submission(self):
        """Retrieve the deposit creation restriction flag."""
        return self.model.restricted_submission

    @property
    def admin_role(self):
        """Role given to this community's administrators."""
        return Role.query.filter(
            Role.name == _community_admin_role_name(self)).one()

    @property
    def member_role(self):
        """Role given to this community's members."""
        return Role.query.filter(
            Role.name == _community_member_role_name(self)).one()


def is_community_role(role):
    """Test if a given role belongs to a community.

    Returns:
        (bool) True if the role belongs to a community
    """
    return len(role.name) > 4 and role.name[:4] == 'com:'


def is_community_admin_role(role):
    """Test if a given role is a community admin role.

    Returns:
        (bool) True if the role is a community admin role.
    """
    name_split = role.name.split(':')
    return is_community_role(role) and len(name_split) == 3 and \
        name_split[2] == 'admin'


def is_community_member_role(role):
    """Test if a given role is a community member role.

    Returns:
        (bool) True if the role is a community member role.
    """
    name_split = role.name.split(':')
    return is_community_role(role) and len(name_split) == 3 and \
        name_split[2] == 'member'


def get_role_community_id(role):
    """Get role's community id.

    Returns:
        uuid: community's id.
    """
    name_split = role.name.split(':')
    if is_community_role(role) and len(name_split) == 3:
        return uuid.UUID(name_split[1])
    else:
        raise NotACommunityRoleError()
