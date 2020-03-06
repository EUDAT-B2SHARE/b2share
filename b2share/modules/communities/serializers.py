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

"""B2Share Communities REST API"""

from flask import jsonify, url_for

from b2share.modules.schemas.api import CommunitySchema
from b2share.modules.schemas.serializers import block_schema_version_self_link, community_schema_json_schema_link
import json


def community_self_link(community, **kwargs):
    """Create self link to a given community.

    Args:
        community (:class:`b2share.modules.communities.api:Community`):
            community to which the generated link will point.

        **kwargs: additional parameters given to flask.url_for.

    :Returns:
        str: link pointing to the given community.
    """
    return url_for(
        'b2share_communities.communities_item',
        community_id=community.id, **kwargs)


def community_to_dict(community):
    ret = dict(
        id=community.id,
        name=community.name,
        description=community.description,
        logo=community.logo,
        created=community.created,
        updated=community.updated,
        publication_workflow=community.publication_workflow,
        restricted_submission=community.restricted_submission,
        links=dict(
            self=community_self_link(community, _external=True),
        ),
        roles=dict(
            admin=dict(id=community.admin_role.id,
                       name=community.admin_role.name,
                       description=community.admin_role.description),
            member=dict(id=community.member_role.id,
                        name=community.member_role.name,
                        description=community.member_role.description),
        )
    )
    try:
        community_schema = CommunitySchema.get_community_schema(community.id)
        community_schema_dict = json.loads(community_schema.community_schema)
        props = community_schema_dict['properties']
        ret['links']['schema'] = community_schema_json_schema_link(community_schema, _external=True)
        ret['links']['block_schema'] = next(iter(props.values()))['$ref']
        ret['schema'] = dict(
            version=community_schema.version,
            block_schema_id=next(iter(props))
        )
    finally:
        return ret

def community_to_json_serializer(community, code=200, headers=None):
    """Build a json flask response using the given community data.

    Returns:
        :class:`flask.Response`: A flask response with json data.
    """
    response = jsonify(community_to_dict(community))
    response.status_code = code
    if headers is not None:
        response.headers.extend(headers)

    response.set_etag(str(community.updated))
    return response


def search_to_json_serializer(data, code=200, headers=None):
    """Build a json flask response using the given search result.

    Returns:
        :class:`flask.Response`: A flask response with json data.
    """
    # TODO
    raise NotImplementedError()
