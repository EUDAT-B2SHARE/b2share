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

from marshmallow import Schema, fields, post_dump
from dateutil.parser import parse
from flask import current_app


class RecordSchemaMarcXMLV1(Schema):
    """Schema for records in MARC."""

    control_number = fields.Method('get_id')

    def get_id(self, obj):
        pids = obj['metadata'].get('_pid')
        p = [p['value'] for p in pids if p['type'] == 'b2share_record']
        return str(p[0])

    date_and_time_of_latest_transaction = fields.Function(
        lambda o: parse(o['updated']).strftime("%Y%m%d%H%M%S.0"))

    information_relating_to_copyright_status = fields.Function(
        lambda o: dict(copyright_status='open' if o['metadata']['open_access'] else 'closed'))

    index_term_uncontrolled = fields.Function(
        lambda o: dict(uncontrolled_term=o['metadata'].get('keywords'))
    )

    terms_governing_use_and_reproduction_note = fields.Function(
        lambda o: dict(terms_governing_use_and_reproduction=o['metadata'].get('license')))

    title_statement = fields.Function(
        lambda o: dict(title=o['metadata'].get('title')))

    other_standard_identifier = fields.Function(
        lambda o: [dict(standard_number_or_code=o['metadata'].get('alternate_identifier'))])

    main_entry_personal_name = fields.Method('get_main_entry_personal_name')

    added_entry_personal_name = fields.Method('get_added_entry_personal_name')

    summary = fields.Function(
        lambda o: dict(summary=o['metadata'].get('description')))

    # Custom fields:

    resource_type = fields.Raw(attribute='metadata.resource_type')

    embargo_date = fields.Raw(attribute='metadata.embargo_date')

    _oai = fields.Raw(attribute='metadata._oai')


    def get_main_entry_personal_name(self, o):
        creators = o['metadata'].get('creators', [])
        if len(creators) > 0:
            return dict(personal_name=creators[0])
        return dict()


    def get_added_entry_personal_name(self, o):
        """Get added_entry_personal_name."""
        items = []
        creators = o['metadata'].get('creators', [])
        if len(creators) > 1:
            for c in creators[1:]:
                items.append(dict(personal_name=c))

        contributors = o['metadata'].get('contributors', [])
        for c in contributors:
            items.append(dict(personal_name=c))

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
