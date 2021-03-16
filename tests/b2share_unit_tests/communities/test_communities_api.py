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

"""Test B2Share communities module's API."""

import pytest
from .helpers import community_metadata, community_patch, community_update, \
    patched_community_metadata, updated_community_metadata
from invenio_db import db
from jsonpatch import InvalidJsonPatch, JsonPatchConflict

from b2share.modules.communities import Community
from b2share.modules.communities.errors import CommunityDeletedError, \
    CommunityDoesNotExistError, InvalidCommunityError


def test_create_community_and_get(app):
    """Test Community.create_community() and Community.get()."""
    with app.app_context():
        # check that getting a nonexistent community raises an exception
        with pytest.raises(CommunityDoesNotExistError):
            Community.get(id='e174feb1-5882-4c1e-bab6-6678f59b993f')
        # test misuse of community.get()
        with pytest.raises(ValueError):
            Community.get(id='e174feb1-5882-4c1e-bab6-6678f59b993f',
                          name='myname')
        with pytest.raises(ValueError):
            Community.get()
    # test invalid community creation
    with app.app_context():
        with pytest.raises(InvalidCommunityError):
            created_community = Community.create_community(name=None,
                                                           description=None,)
    # create a community
    with app.app_context():
        created_community = Community.create_community(**community_metadata)
        community_id = created_community.id
        db.session.commit()
        for field, value in community_metadata.items():
            assert getattr(created_community, field) == value
        assert not created_community.deleted
        assert created_community.created
        assert created_community.updated

    # get the created community
    with app.app_context():
        retrieved_by_id = Community.get(id=community_id)
        retrieved_by_name = Community.get(name=community_metadata['name'])
        assert community_id == retrieved_by_id.id
        assert community_id == retrieved_by_name.id
        for field, value in community_metadata.items():
            assert getattr(retrieved_by_id, field) == value
            assert getattr(retrieved_by_name, field) == value


def test_patch(app):
    """Test Community.patch()."""
    with app.app_context():
        created_community = Community.create_community(**community_metadata)
        community_id = created_community.id
        db.session.commit()

    with app.app_context():
        retrieved = Community.get(id=community_id)
        retrieved.patch(community_patch)
        db.session.commit()

    with app.app_context():
        patched = Community.get(id=community_id)
        assert community_id == patched.id
        assert patched.updated
        for field, value in patched_community_metadata.items():
            assert getattr(patched, field) == value

        # test invalid or conflicting patchs
        with pytest.raises(JsonPatchConflict):
            patched.patch([{
                'op': 'replace',
                'path': '/name',
                'value': 'this should not be applied'
            }, {
                'op': 'replace',
                'path': '/non-existing-field',
                'value': 'random value'
            }])
        with pytest.raises(InvalidJsonPatch):
            patched.patch({'whatever': 'key'})
        with pytest.raises(InvalidCommunityError):
            patched.patch([{
                'op': 'replace',
                'path': '/name',
                'value': None
            }])
        # check that the community was not modified
        for field, value in patched_community_metadata.items():
            assert getattr(patched, field) == value


def test_update(app):
    """Test Community.update()."""
    with app.app_context():
        created_community = Community.create_community(**community_metadata)
        community_id = created_community.id
        db.session.commit()

    with app.app_context():
        retrieved = Community.get(id=community_id)
        retrieved.update(community_update)
        db.session.commit()

    with app.app_context():
        updated = Community.get(id=community_id)
        assert community_id == updated.id
        assert updated.updated
        for field, value in updated_community_metadata.items():
            assert getattr(updated, field) == value

        # test invalid update
        with pytest.raises(InvalidCommunityError):
            updated.update({'name': None})
        # check that the community was not modified
        for field, value in updated_community_metadata.items():
            assert getattr(updated, field) == value


def test_clear_update(app):
    """Test Community.update(clear_fields=True)."""
    with app.app_context():
        created_community = Community.create_community(**community_metadata)
        community_id = created_community.id
        db.session.commit()

    with app.app_context():
        retrieved = Community.get(id=community_id)
        retrieved.update(community_update, clear_fields=True)
        # test invalid update
        with pytest.raises(InvalidCommunityError):
            retrieved.update({}, clear_fields=True)
        db.session.commit()

    with app.app_context():
        updated = Community.get(id=community_id)
        assert community_id == updated.id
        assert updated.updated
        for field, value in updated_community_metadata.items():
            if field not in community_update:
                if field == 'publication_workflow':
                    assert updated.publication_workflow == \
                        'review_and_publish'
                elif field == 'restricted_submission':
                    assert updated.restricted_submission == False
                else:
                    assert getattr(updated, field) is None
            else:
                assert getattr(updated, field) == value


def test_delete(app):
    """Test Community.delete()."""
    with app.app_context():
        created_community = Community.create_community(**community_metadata)
        community_id = created_community.id
        db.session.commit()
    # test deleting a community
    with app.app_context():
        retrieved = Community.get(id=community_id)
        retrieved.delete()
        assert retrieved.deleted
        db.session.commit()
    # test getting a deleted community
    with app.app_context():
        with pytest.raises(CommunityDeletedError):
            Community.get(id=community_id)
    # test force getting a deleted community
    with app.app_context():
        deleted_community = Community.get(id=community_id, with_deleted=True)
        assert deleted_community.deleted
        for field, value in community_metadata.items():
            assert getattr(deleted_community, field) == value
