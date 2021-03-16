# -*- coding: utf-8 -*-
#
# This file is part of EUDAT B2Share.
# Copyright (C) 2016, University of Tuebingen.
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

"""Test B2Share record serializers."""


import pytest
from b2share_unit_tests.helpers import (create_record, create_user)
from b2share.modules.records.serializers import (
    oaipmh_oai_dc, oaipmh_marc21_v1, datacite_v31)
from invenio_indexer.api import RecordIndexer

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


def test_records_serializers_dc(app, test_records_data):
    with app.app_context():
        pid, record = make_record(test_records_data)
        rec = {
            '_source': RecordIndexer()._prepare_record(
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
            '_source': RecordIndexer()._prepare_record(
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
