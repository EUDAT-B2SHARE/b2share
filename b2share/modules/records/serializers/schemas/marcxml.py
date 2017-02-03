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

"""B2Share Records Marc schemas used for serialization."""

from __future__ import absolute_import, print_function

from itertools import chain
from marshmallow import Schema, fields, post_dump
from dateutil.parser import parse
from flask import current_app


class RecordSchemaMarcXMLV1(Schema):
    """Schema for records in MARC."""

    control_number = fields.Method('get_id')

    def get_id(self, obj):
        pids = obj['metadata'].get('_pid')
        p = [p['value'] for p in pids if p['type'] == 'b2rec']
        return str(p[0])

    other_standard_identifier = fields.Method('get_other_standard_identifier')

    date_and_time_of_latest_transaction = fields.Function(
        lambda o: parse(o['updated']).strftime("%Y%m%d%H%M%S.0"))

    main_entry_personal_name = fields.Method('get_main_entry_personal_name')

    added_entry_personal_name = fields.Method('get_added_entry_personal_name')

    title_statement = fields.Function(
        lambda o: o['metadata']['titles'][0])

    publication_distribution_imprint = fields.Function(
        lambda o: dict(name_of_publisher_distributor=o['metadata'].get('publisher'),
                       date_of_publication_distribution=o['metadata'].get('publication_date')))

    media_type = fields.Function(
        lambda o: dict(media_type_term=[x['resource_type_general']
                                        for x in o['metadata'].get('resource_types', [])]))

    summary = fields.Function(
        lambda o: [dict(summary=x.get('description'))
                   for x in o['metadata'].get('descriptions', [])])

    study_program_information_note = fields.Function(
        lambda o: [dict(program_name=o['metadata'].get('disciplines', []))])

    terms_governing_use_and_reproduction_note = fields.Function(
        lambda o: dict(terms_governing_use_and_reproduction=
                       o['metadata'].get('license', {}).get('license'),
                       uniform_resource_identifier=
                       o['metadata'].get('license', {}).get('license_uri')))

    information_relating_to_copyright_status = fields.Function(
        lambda o: dict(copyright_status='open' if o['metadata']['open_access'] else 'closed'))

    language_note = fields.Function(
        lambda o: [dict(language_note=o['metadata'].get('language'))])

    index_term_uncontrolled = fields.Function(
        lambda o: [dict(uncontrolled_term=x) for x in o['metadata'].get('keywords', [])])


    electronic_location_and_access = fields.Function(
        lambda o: [dict(uniform_resource_identifier=f['ePIC_PID'],
                        file_size=str(f['size']),
                        access_method="HTTP")
                   if f.get('ePIC_PID') else None
                   for f in o['metadata'].get('_files', [])])

    # Custom fields:

    embargo_date = fields.Raw(attribute='metadata.embargo_date')

    _oai = fields.Raw(attribute='metadata._oai')


    def get_other_standard_identifier(self, o):
        pids = [p['value'] for p in o['metadata']['_pid']
                if p['type'] in {'ePIC_PID', 'DOI'}]
        alt_ids = [x['alternate_identifier']
                   for x in o['metadata'].get('alternate_identifiers', [])]
        return [dict(standard_number_or_code=x) for x in chain(pids, alt_ids)]


    def get_main_entry_personal_name(self, o):
        creators = o['metadata'].get('creators', [])
        if len(creators) > 0:
            return dict(personal_name=creators[0]['creator_name'])
        return dict()


    def get_added_entry_personal_name(self, o):
        """Get added_entry_personal_name."""
        items = []
        creators = o['metadata'].get('creators', [])
        if len(creators) > 1:
            for c in creators[1:]:
                items.append(dict(personal_name=c['creator_name']))

        contributors = o['metadata'].get('contributors', [])
        for c in contributors:
            items.append(dict(personal_name=c['contributor_name']))

        return items

    @post_dump(pass_many=True)
    def remove_empty_fields(self, data, many):
        """Dump + Remove empty fields."""
        _filter_empty(data)
        return data


def _filter_empty(record):
    """Filter empty fields."""
    if isinstance(record, dict):
        for k in list(record.keys()):
            if record[k]:
                _filter_empty(record[k])
            if not record[k]:
                del record[k]
    elif isinstance(record, list) or isinstance(record, tuple):
        for (k, v) in list(enumerate(record)):
            if v:
                _filter_empty(record[k])
            if not v:
                del record[k]
