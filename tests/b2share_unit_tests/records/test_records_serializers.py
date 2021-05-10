# -*- coding: utf-8 -*-
#
# This file is part of EUDAT B2Share.
# Copyright (C) 2016, University of Tuebingen.
# B2Share is free software; you can redistribute it and/or
#
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

"""Test B2Share record serializers."""


import pytest
import pdb
from b2share_unit_tests.helpers import (create_record, create_user)
from b2share.modules.records.serializers import (
    oaipmh_oai_dc, oaipmh_marc21_v1, datacite_v31, eudatcore_v1, datacite_v44)
from invenio_indexer.api import RecordIndexer
from b2share.modules.records.minters import make_record_url
from b2share.modules.records.serializers.schemas.eudatcore import identifier_prefix

def make_record(test_records_data):
    creator = create_user('creator')
    _, pid, record = create_record(test_records_data[0], creator)
    record['_files'] = [
        {
            'bucket': "15163455-650b-45e5-9b9f-6cf2ef70a08f",
            'checksum': "md5:4653e51dc9b73e020167299ac607e0e1",
            'key': "file1.pptx",
            'size': 26289470,
            'version_id': "389fff57-e6d7-4434-9a44-ca17297be22f",
            'ePIC_PID': "http://hdl.handle.net/1234/15163455-650b-45e5-9b9f-6cf2ef70a08f"
        },
        {
            'bucket': "51163455-650b-45e5-9b9f-6cf2ef70a08f",
            'checksum': "md5:4adfe51dc9b73e020167299ac607e0e1",
            'key': "file2.pptx",
            'size': 1,
            'version_id': "698fff57-e6d7-4434-9a44-ca17297be22f",
            'ePIC_PID': "http://hdl.handle.net/1234/51163455-650b-45e5-9b9f-6cf2ef70a08f"
        }
    ]
    return pid, record

def make_v1_record(test_records_data):
    pid, record = make_record(test_records_data)
    record['spatial_coverages'] = [
            {'place': 'Turku'},
            {'point': {'point_longitude': -20, 'point_latitude': 30}},
            {'box': {
                'westbound_longitude': 60,
                'eastbound_longitude': -30,
                'northbound_latitude': -80,
                'southbound_latitude': 120
                }
            },
            {'polygons': [
                {'polygon': [
                    {'point_latitude': 20, 'point_longitude': 20},
                    {'point_latitude': 30, 'point_longitude': 30},
                    {'point_latitude': 40, 'point_longitude': 40}
                ],
                'inpoint': {
                    'point_latitude': 25,
                    'point_longitude': 25
                }}
                ]
            }
    ]
    record['instruments'] = [{'instrument_name': 'Scalpel'}]
    record['temporal_coverages'] = {
        'ranges': [{'start_date': '1994-04-02', 'end_date': '1994-04-03'}],
        'spans': ['1994-2021']
    }
    record['related_identifiers'] = [
        {'related_identifier_type': 'URL',
         'related_identifier': 'http://www.example.com'}
    ]
    record['license']['scheme'] = 'testScheme'
    record['license']['scheme_uri'] = 'http://www.example.com'
    record['contributors'].append(
        {'contributor_name': 'Doe, John',
        'given_name': 'John',
        'family_name': 'Doe',
        'affiliations': [
            {
                'affiliation_name': 'Fake Org',
                'affiliation_identifier': 'fake_org_id',
                'scheme': 'not_a_real_scheme'
            }
        ],
        'contributor_type': 'DataCurator',
        'name_type': 'Personal',
        'name_identifiers': [
            {'name_identifier': 'totally_a_real_id',
             'scheme': 'actually_not_scheme',
             'scheme_uri': 'http://exmaple.com'}
            ]
        })
    return pid, record


def test_records_serializers_dc(app, test_records_data):
    with app.app_context():
        pid, record = make_record(test_records_data)
        rec = {
            '_source': RecordIndexer._prepare_record(
                record, 'records', 'record'
            ).copy(),
            '_version': record.revision_id
        }
        dcxml = oaipmh_oai_dc(pid=pid, record=rec)

        namespaces = {'dc':'http://purl.org/dc/elements/1.1/'}
        identifiers = dcxml.xpath('//dc:identifier', namespaces=namespaces)
        titles = dcxml.xpath('//dc:title', namespaces=namespaces)
        creators = dcxml.xpath('//dc:creator', namespaces=namespaces)
        descriptions = dcxml.xpath('//dc:description', namespaces=namespaces)
        subjects = dcxml.xpath('//dc:subject', namespaces=namespaces)
        contributors = dcxml.xpath('//dc:contributor', namespaces=namespaces)
        rights = dcxml.xpath('//dc:rights', namespaces=namespaces)
        publishers = dcxml.xpath('//dc:publisher', namespaces=namespaces)
        languages = dcxml.xpath('//dc:language', namespaces=namespaces)
        types = dcxml.xpath('//dc:type', namespaces=namespaces)

        assert identifiers
        for x in identifiers:
            assert x.text.endswith(pid.pid_value)

        assert [x.text for x in titles] == [r['title'] for r in record['titles']]
        assert [x.text for x in creators] == [r['creator_name'] for r in record['creators']]
        assert [x.text for x in descriptions] == [r['description'] for r in record['descriptions']]
        assert [x.text for x in types] == [
            r['resource_type_general'] for r in record['resource_types']]
        assert [x.text for x in contributors] == [
            r['contributor_name'] for r in record['contributors']]
        assert [x.text for x in publishers] == [record['publisher']]
        assert [x.text for x in languages] == [record['language']]

        assert [x.text for x in subjects] == record.get('keywords')

        rights = [x.text for x in rights]
        access = 'info:eu-repo/semantics/closedAccess'
        if record['open_access']:
            access = 'info:eu-repo/semantics/openAccess'
        assert access in rights
        license = record.get('license', {}).get('license')
        if license:
            assert license in rights


def test_records_serializers_marc(app, test_records_data):
    with app.app_context():
        pid, record = make_record(test_records_data)
        rec = {
            '_source': RecordIndexer._prepare_record(
                record, 'records', 'record'
            ).copy(),
            '_version': record.revision_id
        }
        marcxml = oaipmh_marc21_v1(pid=pid, record=rec)

        namespaces = {'m':'http://www.loc.gov/MARC21/slim'}

        def marc_controlfields(tag):
            xpath = '//m:controlfield[@tag="{}"]'.format(tag)
            elements = marcxml.xpath(xpath, namespaces=namespaces)
            return [x.text for x in elements]

        def marc_datafields(tag, subfield_code):
            xpath = '//m:datafield[@tag="{}"]/m:subfield[@code="{}"]'.format(
                tag, subfield_code)
            elements = marcxml.xpath(xpath, namespaces=namespaces)
            return [x.text for x in elements]

        def marc_files():
            xpath = '//m:datafield[@tag="856" and @ind1="4"]/m:subfield[@code="u"]'
            elements = marcxml.xpath(xpath, namespaces=namespaces)
            return [x.text for x in elements]

        creators_and_contributors = [r['creator_name'] for r in record['creators']]
        creators_and_contributors.extend([r['contributor_name']
                                          for r in record['contributors']])

        assert marc_controlfields('001') == [pid.pid_value]

        assert marc_datafields('100', 'a') == creators_and_contributors[:1]
        assert marc_datafields('245', 'a') == [r['title'] for r in record['titles']]
        assert marc_datafields('260', 'b') == [record['publisher']]
        assert marc_datafields('260', 'c') == [record['publication_date']]
        assert marc_datafields('337', 'a') == [
            r['resource_type_general'] for r in record['resource_types']]
        assert marc_datafields('520', 'a') == [r['description'] for r in record['descriptions']]
        assert marc_datafields('526', 'a') == record.get('disciplines')
        assert marc_datafields('540', 'a') == [record.get('license', {}).get('license')]
        assert marc_datafields('542', 'l') == ['open' if record['open_access'] else 'closed']
        assert marc_datafields('546', 'a') == [record['language']]
        assert marc_datafields('653', 'a') == record.get('keywords')
        assert marc_datafields('700', 'a') == creators_and_contributors[1:]

        assert marc_files() == [f['ePIC_PID'] for f in record.get('_files')]


def test_records_serializers_datacite(app, test_records_data):
    with app.app_context():
        import types
        import arrow
        from lxml import etree

        pid, record = make_record(test_records_data)
        def replace_refs(self):
            return self
        record.replace_refs = types.MethodType(replace_refs, record)

        doc_str = datacite_v31.serialize(pid=pid, record=record)
        doc = etree.XML(doc_str.encode('utf-8'))

        namespaces = {'d':'http://datacite.org/schema/kernel-3'}

        def datacite(field):
            xpath = '//d:{}'.format(field)
            elements = doc.xpath(xpath, namespaces=namespaces)
            return [x.text for x in elements]

        assert datacite('creatorName') == [r['creator_name'] for r in record['creators']]
        assert datacite('contributorName') == [
            r['contributor_name'] for r in record['contributors']]
        assert datacite('title') == [r['title'] for r in record['titles']]
        assert datacite('publisher') == [record['publisher']]
        assert datacite('publicationYear') == [str(arrow.get(record['publication_date']).year)]
        assert datacite('description') == [r['description'] for r in record['descriptions']]

        subjects = record.get('disciplines').copy()
        subjects.extend(record.get('keywords'))
        assert datacite('subject') == subjects
        assert datacite('language') == [record['language']]

        assert ('open' if record['open_access'] else 'closed') in datacite('rights')
        license = record.get('license', {}).get('license')
        if license:
            assert license in datacite('rights')

        rt = [{'resource_type_general': x.xpath('@resourceTypeGeneral')[0],
               'resource_type': x.text}
              for x in doc.xpath('//d:resourceType', namespaces=namespaces)]
        assert rt == record['resource_types']

def test_records_serializers_datacite4(app, test_records_data):
    with app.app_context():
        import types
        import arrow
        from lxml import etree

        pid, record = make_v1_record(test_records_data)
        def replace_refs(self):
            return self
        record.replace_refs = types.MethodType(replace_refs, record)
        doc_str = datacite_v44.serialize(pid=pid, record=record)
        doc = etree.XML(doc_str.encode('utf-8'))

        namespaces = {'d':'http://datacite.org/schema/kernel-4.4'}
        def datacite(path):
            return [t.text for t in doc.xpath(path, namespaces=namespaces)]

        assert datacite('//identifier') == [i['value']\
            for i in record['_pid'] if i['type'] == 'DOI']
        assert datacite('//alternateIdentifiers/alternateIdentifier')\
            == [i['value'] for i in record['_pid'] if i['type'] == 'ePIC_PID'] +\
                [i['alternate_identifier'] for i in record['alternate_identifiers']]
        assert datacite('//creators/firstName')\
            == [c['first_name'] for c in record['creators']]
        assert datacite('//creators/familyName')\
            == [c['last_name'] for c in record['creators']]
        assert datacite('//contributors/firstName')\
            == [c['first_name'] for c in record['contributors']]
        assert datacite('//contributors/familyName')\
            == [c['last_name'] for c in record['contributors']]

        assert datacite('//dates/date') == [d['date'] for d in record['dates']]
        assert datacite('//dates/dateType') == [d['date_type'] for d in record['dates']]
        assert datacite('//dates/dateInformation')\
            == [d['date_information'] for d in record['dates']]

        assert datacite('//relatedIdentifiers/relatedIdentifier')\
            == [i['related_identifier'] for i in record['related_identifiers']]

        rights = [t.text for t in doc.xpath('//rightsList/rights')]
        assert ('open' if record['open_access'] else 'closed') in rights
        license = record.get('license', {})
        if license:
            assert license.get('license') in rights
            assert license.get('scheme_uri') in datacite('//rightsList/rights/@schemeURI')
            assert license.get('scheme') in datacite('//rightsList/rights/@scheme')
        assert datacite('//description') == [d['description'] for d in record['descriptions']]
        assert datacite('//description/@descriptionType')\
            == [d['description_type'] for d in record['descriptions']]
        assert datacite('//geoLocations/geoLocation/geoLocationBox/*')\
            == [record['spatial_coverages'][0]['box'][k] for k in\
            ['westbound_longitude', 'eastbound_longitude', 'northbound_latitude', 'southbound_latitude']]
        assert datacite('//geoLocations/geoLocation/geoLocationPlace')\
            == [record['spatial_coverages'][0]['place']]
        assert datacite('//geoLocations/geoLocation/geoLocationPoint/*')\
            == [record['spatial_coverages'][0]['point'][k] for k in ['point_longitude', 'point_latitude']]
        assert datacite('//geoLocations/geoLocation/geoLocationPolygon/polygonPoint/pointLongitude')\
            == [p['point_longitude'] for p in record['spatial_coverages'][0]['polygons'][0]['polygon']]
        assert datacite('//geoLocations/geoLocation/geoLocationPolygon/polygonPoint/pointLatitude')\
            == [p['point_latitude'] for p in record['spatial_coverages'][0]['polygons'][0]['polygon']]
        assert datacite('//geoLocations/geoLocation/geoLocationPolygon/inPolygonPoint/*')\
            == [record['spatial_coverages'][0]['polygons'][0]['inpoint'][k] for k in ['point_longitude', 'point_latitude']]

        assert datacite('//contributors//familyName') == [c['family_name'] for c in record['contributors'] if c.get('family_name')]
        assert datacite('//contributors//nameIdentifier/') == [c['name_identifier'] for c in record['contributors'] if c.get('name_identifier')]
        affiliations = []
        for c in record['contributors']:
            if c.get('affiliations'):
                for a in c['affiliations']:
                    affiliations.append(a)
        assert datacite('//contributors//affiliation/@affiliationIdentifier') == [a['affiliation_identifier'] for a in affiliations]
        assert datacite('//contributors//affililiation') == [a['affiliation_name'] for a in affiliations]


def test_records_serializers_eudatcore(app, test_records_data):
    with app.app_context():
        import types
        pid, record = make_v1_record(test_records_data)
        def replace_refs(self):
            return self
        record.replace_refs = types.MethodType(replace_refs, record)
        xml = eudatcore_v1(pid=pid, record=record)

        assert [t.text for t in xml.xpath('//titles/title')] == \
            [t['title'] for t in record['titles']]
        assert xml.xpath('//community')[0].text == 'MyTestCommunity1'
        assert [t.text for t in xml.xpath('//identifiers')[0].xpath('//identifier')] == [
            'pid:{}'.format(record['_pid'][2]['value']),
            'doi:{}'.format(record['_pid'][3]['value']),
            'url:{}'.format(make_record_url(record['_pid'][1]['value']))
        ]
        assert [t.text for t in xml.xpath('//publishers')[0].xpath('//publisher')] == [
            'EUDAT B2SHARE',
            record['publisher']
        ]
        assert xml.xpath('//publicationYear')[0].text == record['publication_date'][:4]
        assert [c.text for c in xml.xpath('//creators/creator')] == \
            [c['creator_name'] for c in record['creators']]
        assert [i.text for i in xml.xpath('//instruments/instrument')] == \
            [i['instrument_name'] for i in record['instruments']]
        assert [s.text for s in xml.xpath('//subjects/subject')] == record['keywords']
        assert [d.text for d in xml.xpath('//disciplines/discipline')] == record['disciplines']
        assert [c.text for c in xml.xpath('//contributors/contributor')] == \
            [c['contributor_name']for c in record['contributors']]
        assert [f.text for f in xml.xpath('//formats/format')] == \
            list(set([f['key'].split('.')[1] for f in record['_files']]))
        assert [i.text for i in xml.xpath('//alternateIdentifiers/alternateIdentifier')] == \
            ["{}{}".format(identifier_prefix(i['alternate_identifier_type']), i['alternate_identifier'])\
                for i in record['alternate_identifiers']]
        assert [i.text for i in xml.xpath('//relatedIdentifiers/relatedIdentifier')] == \
            ["{}{}".format(identifier_prefix(i['related_identifier_type']), i['related_identifier']) \
                for i in record['related_identifiers']]
        assert xml.xpath('//spatialCoverages/spatialCoverage/geoLocationPlace')[0].text == 'Turku'
        assert xml.xpath('//spatialCoverages/spatialCoverage/geoLocationPoint/pointLongitude')[0]\
        .text == '-20'
        assert xml.xpath('//spatialCoverages/spatialCoverage/geoLocationPoint/pointLatitude')[0]\
        .text == '30'
        assert xml.xpath(
            '//spatialCoverages/spatialCoverage/geoLocationBox/westBoundLongitude'
            )[0].text == '60'
        assert xml.xpath(
            '//spatialCoverages/spatialCoverage/geoLocationBox/eastBoundLongitude'
        )[0].text == '-30'
        assert xml.xpath(
            '//spatialCoverages/spatialCoverage/geoLocationBox/northBoundLatitude'
        )[0].text == '-80'
        assert xml.xpath(
            '//spatialCoverages/spatialCoverage/geoLocationBox/southBoundLatitude'
        )[0].text == '120'
        assert [e.text for e in xml.xpath(
            '//spatialCoverages/spatialCoverage/geoLocationPolygon/polygonPoint/pointLatitude'
        )] == ['20', '30', '40']
        assert [e.text for e in xml.xpath(
            '//spatialCoverages/spatialCoverage/geoLocationPolygon/polygonPoint/pointLongitude'
        )] == ['20', '30', '40']
        assert [e.text for e in xml.xpath(
            '//spatialCoverages/spatialCoverage/geoLocationPolygon/inPolygonPoint/pointLongitude'
        )] == ['25']
        assert [e.text for e in xml.xpath(
            '//spatialCoverages/spatialCoverage/geoLocationPolygon/inPolygonPoint/pointLatitude'
        )] == ['25']
        assert xml.xpath(
            '//temporalCoverages/temporalCoverage/startDate'
        )[0].text == '1994-04-02'
        assert xml.xpath('//temporalCoverages/temporalCoverage/endDate')[0].text == '1994-04-03'
        assert xml.xpath('//temporalCoverages/temporalCoverage/span')[0].text == '1994-2021'
