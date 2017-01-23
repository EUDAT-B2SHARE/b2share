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


datacite_v3_description_types = set([
    "Abstract", "Methods", "SeriesInformation", "TableOfContents"])


class IdentifierSchema(Schema):
    """Identifier schema."""

    def get_doi(self, pids):
        p = [p['value'] for p in pids if p['type'] == 'DOI']
        return str(p[0]) if p else None

    identifier = fields.Method('get_doi')
    identifierType = fields.Constant('DOI')


class AlternateIdentifierSchema(Schema):
    def get_pid(self, pids):
        p = [p['value'] for p in pids if p['type'] == 'ePIC_PID']
        return str(p[0])

    alternateIdentifier = fields.Method('get_pid')
    alternateIdentifierType = fields.Constant('ePIC_PID')


class DataCiteSchemaV1(Schema):
    # --- required
    identifier = fields.Nested(IdentifierSchema, attribute='metadata._pid')

    creators = fields.Method('get_creators')
    titles = fields.Function(lambda o: o['metadata'].get('titles'))

    publisher = fields.Function(
        lambda o: o['metadata'].get('publisher', "").strip() or 'https://b2share.eudat.eu')
    publicationYear = fields.Method('get_publication_year')
    resourceType = fields.Method('get_resource_type')

    # --- optional
    subjects = fields.Method('get_subjects')
    contributors = fields.Method('get_contributors')
    language = fields.Str(attribute='metadata.language')
    alternateIdentifiers = fields.List(
        fields.Nested(AlternateIdentifierSchema, attribute='metadata._pid'))
    rightsList = fields.Method('get_rights')
    descriptions = fields.Method('get_descriptions')

    def get_creators(self, obj):
        crs = obj['metadata'].get('creators') or [{'creator_name':'[Unknown]'}]
        return [{'creatorName':c['creator_name']} for c in crs]

    def get_publication_year(self, obj):
        # datacite: "The year when the data has been or will be made public"
        m = obj['metadata']
        date = m.get('publication_date') or m.get('embargo_date') or obj['created']
        return str(arrow.get(date).year)

    def get_resource_type(self, obj):
        rt_list = obj['metadata'].get('resource_types', [])
        if len(rt_list) == 0:
            return {'resourceTypeGeneral':'Other'}
        rt = rt_list[0]
        ret = {'resourceTypeGeneral': rt['resource_type_general']}
        if rt.get('resource_type'):
            ret['resourceType'] = rt['resource_type']
        return ret

    def get_subjects(self, obj):
        items = []
        disciplines = obj['metadata'].get('disciplines', [])
        for d in disciplines:
            items.append({'subject': d})
        for s in obj['metadata'].get('keywords', []):
            items.append({'subject': s})
        return items

    def get_rights(self, obj):
        """Get rights."""
        open_access = obj['metadata'].get('open_access')
        access_uri = 'info:eu-repo/semantics/openAccess' if open_access \
            else 'info:eu-repo/semantics/closedAccess'
        rights = [{"rightsURI": access_uri,
                   "rights": 'open'if open_access else 'closed'}]
        license = obj['metadata'].get('license')
        if license and 'license_uri' in license:
            rights.append({"rightsURI": license.get('license_uri'),
                           "rights": license.get('license')})
        return rights

    def get_contributors(self, obj):
        return [{'contributorName': c['contributor_name'],
                 'contributorType': c['contributor_type']}
                for c in obj['metadata'].get('contributors', [])]

    def get_descriptions(self, obj):
        return [{'description': d['description'],
                 'descriptionType': d['description_type']
                                    if d['description_type'] in datacite_v3_description_types
                                    else "Other"}
                for d in obj['metadata'].get('descriptions', [])]

