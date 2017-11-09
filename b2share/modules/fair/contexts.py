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

"""Fair Data Point Contexts."""

from marshmallow import Schema, fields

FDP_CONTEXT = {
    '@context': {
        "dct":"http://purl.org/dc/terms/",
        "description":"dct:description",
        "identifier":"dct:identifier"
    }        
}

FDP_CONTEXT2 = {
    '@context': {
        "dct": "http://purl.org/dc/terms/",
        '@base': 'http://localhost/record/',
        'recid': '@id',
        'title': 'dct:title'
    }
}


class _FDPSchema(Schema):
    """FDP Schema"""
    identifier = fields.Str()
    description = fields.Str()
    

class _TestSchema(Schema):
    """Test schema."""

    title = fields.Str(attribute='metadata.title')
    recid = fields.Str(attribute='metadata.recid')
    id = fields.Str(attribute='pid.pid_value')
