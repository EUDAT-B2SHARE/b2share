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

"""B2Share Records DC schemas used for serialization."""

from __future__ import absolute_import, print_function

from marshmallow import Schema, fields, pre_dump
from flask import url_for


def md_getter_as_list(attribute):
    return lambda record: [record['metadata'].get(attribute)]

def md_getter(attribute):
    return lambda record: record['metadata'].get(attribute, [])

def md_subgetter_as_list(attribute, subattribute):
    return lambda record: [x.get(subattribute) for x in record['metadata'].get(attribute, [])]


def record_url(pid_value):
    return url_for('b2share_records_rest.b2rec_item',
        pid_value=pid_value, _external=True)

class RecordSchemaDublinCoreV1(Schema):
    """Schema for Dublin Core conversions."""

    identifiers = fields.Method('get_identifiers')

    titles = fields.Function(md_subgetter_as_list('titles', 'title'))
    creators = fields.Function(md_subgetter_as_list('creators', 'creator_name'))
    descriptions = fields.Function(md_subgetter_as_list('descriptions', 'description'))
    subjects = fields.Function(md_getter('keywords'))
    contributors = fields.Function(md_subgetter_as_list('contributors', 'contributor_name'))
    types = fields.Function(md_subgetter_as_list('resource_types', 'resource_type_general'))

    rights = fields.Method('get_rights')
    dates = fields.Method('get_dates')
    publishers = fields.Function(md_getter_as_list('publisher'))
    languages = fields.Function(md_getter_as_list('language'))

    def get_identifiers(self, obj):
        """Get identifiers."""
        items = [p['value']
                 for p in obj['metadata'].get('_pid', {})
                 if p['type'] in {'ePIC_PID', 'DOI'}]
        items.extend([record_url(p['value'])
                      for p in obj['metadata'].get('_pid', {})
                      if p['type'] == 'b2rec'])
        oai = obj['metadata'].get('_oai', {}).get('id')
        if oai:
            items.append(oai)
        return items

    def get_rights(self, obj):
        """Get rights."""
        open_access = obj['metadata'].get('open_access')
        access = 'info:eu-repo/semantics/openAccess' if open_access \
            else 'info:eu-repo/semantics/closedAccess'
        rights = [access]
        license = obj['metadata'].get('license',{}).get('license')
        if license:
            rights.append(license)
        return rights

    def get_dates(self, obj):
        """Get dates."""
        dates = [obj['created']]
        embargo = obj['metadata'].get('embargo_date')
        if embargo:
            dates.append('info:eu-repo/date/embargoEnd/{0}'.format(embargo))

        return dates
