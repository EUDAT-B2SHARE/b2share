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

"""Test data for b2share schemas."""

communities_metadata = [
    {
        'name': 'mycommunity 1',
        'description': 'My community 1 description',
    }, {
        'name': 'mycommunity 2',
        'description': 'My community 2 description',
    },
]

root_schemas_json_schemas = [{
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'type': 'object',
    'properties': {
        'authors': {
            'type': 'array',
            'items': {'type': 'string'}
        },
        'community_specific': {'type': 'object'},
    },
    'required': ['authors'],
    'additionalProperties': False,
}, {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'type': 'object',
    'properties': {
        'authors': {
            'type': 'array',
            'items': {'type': 'string'}
        },
        'community_specific': {'type': 'object'},
        'files': {
            'type': 'array',
            'items': {'type': 'string'},
        },
    },
    'required': ['authors', 'files'],
    'additionalProperties': False,
}]


backward_incompatible_root_schemas_json_schemas = [{
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'type': 'object',
    'properties': {
        'authors': {
            'type': 'object',
            'properties': {
                'name': {'type': 'string'}
            }
        }
    },
    'additionalProperties': False,
}, {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'type': 'object',
    'properties': {
        'files': {
            'type': 'array',
            'items': {'type': 'number'}
        }
    },
    'additionalProperties': False,
}]
"""Schemas which are not backward compatible with root_schemas_json_schemas"""

block_schemas_json_schemas = [[
    {
        '$schema': 'http://json-schema.org/draft-04/schema#',
        'type': 'object',
        'properties': {
            'experiment_nb': {'type': 'number'},
        },
        'additionalProperties': False,
    },
    {
        '$schema': 'http://json-schema.org/draft-04/schema#',
        'type': 'object',
        'properties': {
            'experiment_nb': {'type': 'number'},
            'experiment_date': {'type': 'string'},
        },
        'required': ['experiment_date'],
        'additionalProperties': False,
    },

], [
    {
        '$schema': 'http://json-schema.org/draft-04/schema#',
        'type': 'object',
        'properties': {
            'analysis_result': {'type': 'string'},
        },
        'additionalProperties': False,
    },
]]


backward_incompatible_block_schemas_json_schemas = [
    {
        '$schema': 'http://json-schema.org/draft-04/schema#',
        'type': 'object',
        'properties': {
            'experiment_nb': {'type': 'string'},
        },
        'additionalProperties': False,
    },
    {
        '$schema': 'http://json-schema.org/draft-04/schema#',
        'type': 'object',
        'properties': {
            'experiment_date': {'type': 'object'},
        },
        'additionalProperties': False,
    },

]
