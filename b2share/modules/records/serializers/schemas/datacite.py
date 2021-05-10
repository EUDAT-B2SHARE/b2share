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

datacite_v4_description_types = set([
    "Abstract", "Methods", "SeriesInformation", "TableOfContents", "TechnicalInfo, Other"])

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

    # --- optional
    resourceType = fields.Method('get_resource_type')
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
            return []
        rt = rt_list[0]
        if rt.get('resource_type_general'): # root schema v0
            ret = {'resourceTypeGeneral': rt['resource_type_general']}
            if rt.get('resource_type'):
                ret['resourceType'] = rt['resource_type']
        else:                             # root schema v1
            ret = {'resourceTypeGeneral': rt['resource_type']}
            if rt.get('resource_description'):
                ret['resourceType'] = rt['resource_description']
        return ret

    def get_subjects(self, obj):
        items = []
        disciplines = obj['metadata'].get('disciplines', [])
        for d in disciplines:
            if isinstance(d, str):
                items.append({'subject': d})
            elif 'discipline_name' in d:
                items.append({'subject': d['discipline_name']})
        for s in obj['metadata'].get('keywords', []):
            if isinstance(s, str):
                items.append({'subject': s})
            elif 'keyword' in s:
                items.append({'subject': s['keyword']})
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

## helper functions for DataCite 4

def camelcase(s):
    if 'bound' in s:
        s = s.replace('bound', '_bound')
    s = s.split('_')
    return s[0] + ''.join([p.capitalize() for p in s[1:]])

def transform_to_camelcase(obj):
    ret = {}
    for key in obj:
        ret[camelcase(key)] = obj[key]
    return ret

def add_names_and_affiliations(obj, field_name, ret):
    field = obj['metadata'].get(field_name, [])
    for i in range(len(field)):
        c = field[i]
        if c.get('given_name'):
            ret[i]['givenName'] = c['given_name']
        if c.get('family_name'):
            ret[i]['familyName'] = c['family_name']
        if c.get('name_type'):
            ret[i]['nameType'] = c['name_type']
        if c.get('affiliations'):
            affiliations = []
            for a in c['affiliations']:
                affiliation = {'name': a['affiliation_name']}
                if a.get('affiliation_identifier'):
                    affiliation['affiliationIdentifier'] = a['affiliation_identifier']
                if a.get('scheme'):
                    affiliation['affiliationIdentifierScheme'] = a['scheme']
                affiliations.append(affiliation)
            ret[i]['affiliation'] = affiliations
        if c.get('name_identifiers'):
            nameIdentifiers = []
            for n in c['name_identifiers']:
                nameId = transform_to_camelcase(n)
                nameId['nameIdentifierScheme'] = n['scheme']
                nameIdentifiers.append(nameId)
            ret[i]['nameIdentifiers'] = nameIdentifiers
    return ret

class DataCiteSchemaV2(DataCiteSchemaV1):
    def get_identifiers(self, obj):
        return [{'identifier': i['value'], 'identifierType': i['type']}\
            for i in obj['metadata']['_pid'] if i['type'] == 'DOI']

    def get_creators(self, obj):
        ret = [{'name': c['creatorName']} for c in super().get_creators(obj)]
        return add_names_and_affiliations(obj, 'creators', ret)

    def get_contributors(self, obj):
        return add_names_and_affiliations(obj, 'contributors', [{'name': c['contributor_name'],\
            'contributorType': c['contributor_type']} for c in obj['metadata'].get('contributors', [])])

    def get_dates(self, obj):
        ret = []
        if obj['metadata'].get('embargo_date'):
            ret.append({'date': obj['metadata']['embargo_date'], 'dateType': 'Available'})
        elif obj['metadata'].get('publication_date'):
            ret.append({'date': obj['metadata']['publication_date'], 'dateType': 'Available'})
        ret.append({'date': obj['created'], 'dateType': 'Submitted'})
        return ret

    def get_subjects(self, obj):
        ret = super().get_subjects(obj)
        dk = obj['metadata'].get('disciplines', []) + obj['metadata'].get('keywords', [])
        for i in range(len(dk)):
            if isinstance(dk[i], str):
                continue
            if dk[i].get('scheme'):
                ret[i]['subjectScheme'] = dk[i]['scheme']
            if dk[i].get('scheme_uri'):
                ret[i]['schemeUri'] = dk[i]['scheme_uri']
        return ret

    def get_alternate_identifiers(self, obj):
        return [{'alternateIdentifier': i['value'], 'alternateIdentifierType': i['type']}\
            for i in obj['metadata']['_pid'] if i['type'] == 'ePIC_PID']\
            + [transform_to_camelcase(a) for a in obj['metadata'].get('alternate_identifiers', [])]

    def get_related_identifiers(self, obj):
        return [transform_to_camelcase(i) for i in obj['metadata'].get('related_identifiers', [])]

    def get_rights(self, obj):
        ret = super().get_rights(obj)
        license = obj['metadata'].get('license')
        if license:
            if license.get('license_identifier'):
                ret[1]['rightsIdentifier'] = license['license_identifier']
            if license.get('scheme'):
                ret[1]['rightsIdentifierScheme'] = license['scheme']
            if license.get('scheme_uri'):
                ret[1]['schemeUri'] = license['scheme_uri']
        return ret

    def get_descriptions(self, obj):
        return [{'description': d['description'],
                 'descriptionType': d['description_type']
                                    if d['description_type'] in datacite_v4_description_types
                                    else "Other"}
                for d in obj['metadata'].get('descriptions', [])]

    def get_geolocations(self, obj):
        ret = []

        def transform_polygon(p):
            ret = {'polygonPoints': [transform_to_camelcase(p) for p in p.get('polygon', [])]}
            if 'inpoint' in p:
                ret['inPolygonPoint'] = transform_to_camelcase(p['inpoint'])
            return ret

        for sc in obj['metadata'].get('spatial_coverages', []):
            geoloc = {}
            if 'place' in sc:
                geoloc['geoLocationPlace'] = sc['place']
            if 'point' in sc:
                geoloc['geoLocationPoint'] = transform_to_camelcase(sc['point'])
            if 'box' in sc:
                geoloc['geoLocationBox'] = transform_to_camelcase(sc['box'])
            if 'polygons' in sc:
                geoloc['geoLocationPolygons'] = [transform_polygon(p) for p in [p for p in sc['polygons'] if len(p.get('polygon', [])) > 3]]
            ret.append(geoloc)
        return ret

    def get_funding_references(self, obj):
        ret = []
        for fr in obj['metadata'].get('funding_references', []):
            ret.append(transform_to_camelcase(fr))
        return ret

    def get_resource_type(self, obj):
        rt_list = obj['metadata'].get('resource_types', [])
        if len(rt_list) == 0:
            return {'resourceTypeGeneral': 'Dataset', 'resourceType': ''}
        rt = rt_list[0]
        if rt.get('resource_type_general'): # root schema v0
            ret = {'resourceTypeGeneral': rt['resource_type_general'], 'resourceType': ''}
            if rt.get('resource_type'):
                ret['resourceType'] = rt['resource_type']
        else:                             # root schema v1
            ret = {'resourceTypeGeneral': rt['resource_type'], 'resourceType': ''}
            if rt.get('resource_description'):
                ret['resourceType'] = rt['resource_description']
        return ret

    def get_language(self, obj):
        return obj['metadata'].get('languages', []).get(0, '')

    def get_sizes(self, obj):
        from .eudatcore import human_readable_size
        n_files = 0
        total_size = 0
        for f in obj['metadata']['_files']:
            total_size += f['size']
            n_files += 1
        return ['{} file{}'.format(n_files, 's' if n_files>1 else ''), human_readable_size(total_size)]

    def get_formats(self, obj):
        formats = set()
        ret = False
        for f in obj['metadata'].get('_files', []):
            split = f.get('key', '').split('.')
            if len(split) > 1:
                ret = True
                formats.add(split[len(split)-1])
        return list(formats)

    identifiers = fields.Method('get_identifiers')
    types = fields.Method('get_resource_type')
    subjects = fields.Method('get_subjects')
    contributors = fields.Method('get_contributors')
    language = fields.Method('get_language')
    sizes = fields.Method('get_sizes')
    version = fields.Str(attribute='metadata.version')
    rightsList = fields.Method('get_rights')
    descriptions = fields.Method('get_descriptions')
    creators = fields.Method('get_creators')
    titles = fields.Function(lambda o: o['metadata'].get('titles'))
    publisher = fields.Function(
        lambda o: o['metadata'].get('publisher', "").strip() or 'https://b2share.eudat.eu')
    publicationYear = fields.Method('get_publication_year')
    dates = fields.Method('get_dates')
    alternateIdentifiers = fields.Method('get_alternate_identifiers')
    relatedIdentifiers = fields.Method('get_related_identifiers')
    geoLocations = fields.Method('get_geolocations')
    fundingReferences = fields.Method('get_funding_references')