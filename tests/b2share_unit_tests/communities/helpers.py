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

"""Tests helpers and common data."""

import json
from copy import deepcopy

from flask import url_for
from jsonpatch import apply_patch
from six import string_types

community_metadata = {
    'name': 'newcommunity',
    'description': 'A new community',
    'logo': 'http://example.com/logo',
    'publication_workflow': 'review_and_publish',
    'restricted_submission': False,
}

community_patch = [
    {'op': 'replace', 'path': '/name', 'value': 'patched name'},
    {'op': 'replace', 'path': '/description', 'value': 'patched description'},
]

community_json_diff = dict(
    name='patched name',
    description='patched description'
)
"""Used for patch with a json data."""

patched_community_metadata = apply_patch(community_metadata, community_patch)

community_update = {
    'name': 'updated name',
    'description': 'updated description',
}

updated_community_metadata = deepcopy(community_metadata)
updated_community_metadata.update(community_update)


def patch_with_json_patch(community_id, client):
    """Request a PATCH of a community with a json-patch."""
    headers = [('Content-Type', 'application/json-patch+json'),
               ('Accept', 'application/json')]
    return client.patch(url_for('b2share_communities.communities_item',
                                community_id=community_id),
                        data=json.dumps(community_patch),
                        headers=headers)


def patch_with_json_diff(community_id, client):
    """Request a PATCH of a community with a json diff."""
    headers = [('Content-Type', 'application/json'),
               ('Accept', 'application/json')]
    return client.patch(url_for('b2share_communities.communities_item',
                                community_id=community_id),
                        data=json.dumps(community_json_diff),
                        headers=headers)
