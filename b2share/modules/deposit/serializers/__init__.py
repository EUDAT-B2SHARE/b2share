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

"""B2Share serializers."""

from __future__ import absolute_import, print_function

from b2share.modules.records.serializers.schemas.json import DraftSchemaJSONV1

from b2share.modules.records.serializers.response import \
    record_responsify, search_responsify, JSONSerializer

json_v1 = JSONSerializer(DraftSchemaJSONV1)
json_v1_response = record_responsify(json_v1, 'application/json')
json_v1_search = search_responsify(json_v1, 'application/json')
