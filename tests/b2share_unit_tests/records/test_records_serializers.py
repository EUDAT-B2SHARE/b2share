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


from b2share_unit_tests.helpers import (create_record, create_user)
from b2share.modules.records.serializers import (
    oaipmh_oai_dc, oaipmh_marc21_v1, datacite_v31)

def test_records_serializers_dc(app, test_records_data):
    with app.app_context():
        creator = create_user('creator')
        _, pid, record = create_record(test_records_data[0], creator)

        rec = {'_source': record.copy(), '_version': 1}
        dcxml = oaipmh_oai_dc(pid=pid, record=rec)

        namespaces = {'dc':'http://purl.org/dc/elements/1.1/'}
        identifiers = dcxml.xpath('//dc:identifier', namespaces=namespaces)
        titles = dcxml.xpath('//dc:title', namespaces=namespaces)
        creators = dcxml.xpath('//dc:creator', namespaces=namespaces)
        descriptions = dcxml.xpath('//dc:description', namespaces=namespaces)
        subjects = dcxml.xpath('//dc:subject', namespaces=namespaces)
        contributors = dcxml.xpath('//dc:contributor', namespaces=namespaces)
        dates = dcxml.xpath('//dc:date', namespaces=namespaces)
        rights = dcxml.xpath('//dc:rights', namespaces=namespaces)
        publishers = dcxml.xpath('//dc:publisher', namespaces=namespaces)
        languages = dcxml.xpath('//dc:language', namespaces=namespaces)
        types = dcxml.xpath('//dc:type', namespaces=namespaces)

        # import ipdb; ipdb.set_trace()
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
        if record.get('license'):
            assert record.get('license') in [x.text for x in rights]
