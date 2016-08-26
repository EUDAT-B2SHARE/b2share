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
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""JSON resolver for JSON schemas."""

from __future__ import absolute_import, print_function

import jsonresolver
from werkzeug.routing import Rule

from .api import BlockSchema, CommunitySchema
from .serializers import block_schema_version_to_dict, community_schema_to_dict


@jsonresolver.hookimpl
def jsonresolver_loader(url_map):
    """JSON resolver plugin.
    Injected into Invenio-Records JSON resolver.
    """
    from flask import current_app

    def block_schema_resolver(schema_id, schema_version_nb):
        block_schema = BlockSchema.get_block_schema(schema_id)
        block_schema_version = block_schema.versions[schema_version_nb]
        return block_schema_version_to_dict(block_schema_version)

    def community_resolver(community_id, schema_version_nb):
        community_schema = CommunitySchema.get_community_schema(
            community_id=community_id,
            version=schema_version_nb)
        return community_schema_to_dict(community_schema)

    url_map.add(Rule(
        '{}/communities/<string:community_id>/schemas/'
        '<int:schema_version_nb>'.format(
            current_app.config.get('APPLICATION_ROOT') or ''),
        endpoint=community_resolver,
        host=current_app.config['JSONSCHEMAS_HOST']))

    url_map.add(Rule(
        '{}/schemas/<string:schema_id>/versions'
        '/<int:schema_version_nb>'.format(
            current_app.config.get('APPLICATION_ROOT') or ''),
        endpoint=block_schema_resolver,
        host=current_app.config['JSONSCHEMAS_HOST']))
