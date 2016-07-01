# -*- coding: utf-8 -*-
#
# This file is part of EUDAT B2Share.
# Copyright (C) 2016 University of Tuebingen, CERN.
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

"""B2Share Records JSON schemas used for serialization."""

from marshmallow import Schema, fields, pre_dump


class DraftSchemaJSONV1(Schema):
    """Schema for records v1 in JSON."""

    id = fields.String(attribute='pid.pid_value')
    metadata = fields.Raw()
    links = fields.Raw()
    created = fields.Str()
    updated = fields.Str()

    @pre_dump
    def filter_internal(self, data):
        """Remove internal fields from the record metadata."""
        data['metadata']['owners'] = data['metadata']['_deposit']['owners']
        del data['metadata']['_deposit']
        if '_files' in data['metadata']:
            del data['metadata']['_files']
        if '_pid' in data['metadata']:
            del data['metadata']['_pid']
        return data


class RecordSchemaJSONV1(DraftSchemaJSONV1):
    """Schema for drafts v1 in JSON."""
