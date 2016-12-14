# -*- coding: utf-8 -*-
#
# This file is part of EUDAT B2Share.
# Copyright (C) 2016 CERN, University of Tuebingen.
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

"""Record serialization for DOIs."""

from __future__ import absolute_import, print_function

import json

import arrow
from marshmallow import Schema, fields

class IdentifierSchema(Schema):
    """Identifier schema."""

    def get_doi(self, pids):
        p = [p['value'] for p in pids if p['type'] == 'DOI_RESERVED']
        return str(p[0])

    identifier = fields.Method('get_doi')
    identifierType = fields.Constant('DOI')


class AlternateIdentifierSchema(Schema):
    def get_pid(self, pids):
        p = [p['value'] for p in pids if p['type'] == 'ePIC_PID']
        return str(p[0])

    alternateIdentifier = fields.Method('get_pid')
    alternateIdentifierType = fields.Constant('handle')


class DataCiteSchemaV1(Schema):
    # --- required
    identifier = fields.Nested(IdentifierSchema, attribute='metadata._pid')
    creators = fields.Method('get_creators')
    titles = fields.Function(
        lambda o: [{'title':o['metadata'].get('title')}])

    # Publisher: The name of the entity that holds, archives, publishes
    #       prints, distributes, releases, issues, or produces the resource.
    #       This property will be used to formulate the citation, so consider
    #       the prominence of the role.
    #         Examples: World Data Center for Climate (WDCC);
    #                   GeoForschungsZentrum Potsdam (GFZ);
    #                   Geological Institute, University of Tokyo
    publisher = fields.Function(
        lambda o: o['metadata'].get('publisher') or 'https://b2share.eudat.eu')

    publicationYear = fields.Method('get_publication_year')
    resourceType = fields.Method('get_resource_type')

    # --- optional
    subjects = fields.Method('get_subjects')
    contributors = fields.Method('get_contributors')
    language = fields.Str(attribute='metadata.language')
    alternateIdentifiers = fields.List(
        fields.Nested(AlternateIdentifierSchema, attribute='metadata._pid'))
    rightsList = fields.List(fields.Function(
        lambda o: {'rights': o['metadata'].get('license')}))
    descriptions = fields.Method('get_descriptions')

    def get_creators(self, obj):
        crs = obj['metadata'].get('creators', ['[Unknown]'])
        return [{'creatorName':c} for c in crs]

    def get_publication_year(self, obj):
        # datacite: "The year when the data has been or will be made public"
        date = obj['metadata'].get('embargo_date') or obj['created']
        return str(arrow.get(date).year)

    def get_resource_type(self, obj):
        rt_list = obj['metadata'].get('resource_type', [])
        rt = rt_list[0] if (rt_list and rt_list[0]) else "Other"
        return {'resourceTypeGeneral': rt}

    def get_subjects(self, obj):
        items = []
        discipline = obj['metadata'].get('discipline')
        if discipline:
            items.append({'subject': discipline})
        for s in obj['metadata'].get('keywords', []):
            items.append({'subject': s})
        return items

    def get_contributors(self, obj):
        return [{'contributorName': c, 'contributorType': 'Other'}
                for c in obj['metadata'].get('contributors', [])]

    def get_descriptions(self, obj):
        items = []
        desc = obj['metadata'].get('description')
        if desc:
            items.append({
                'description': desc,
                'descriptionType': 'Abstract'
            })
        return items
