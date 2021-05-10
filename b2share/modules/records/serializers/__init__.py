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

from invenio_records_rest.serializers.response import search_responsify
from invenio_records_rest.serializers.dc import DublinCoreSerializer
from invenio_records_rest.serializers.datacite import DataCite31Serializer, BaseDataCiteSerializer

from dojson.contrib.to_marc21 import to_marc21
from invenio_marc21.serializers.marcxml import MARCXMLSerializer

from b2share.modules.records.serializers.schemas.json import RecordSchemaJSONV1
from b2share.modules.records.serializers.schemas.dc import RecordSchemaDublinCoreV1
from b2share.modules.records.serializers.schemas.marcxml import RecordSchemaMarcXMLV1
from b2share.modules.records.serializers.schemas.datacite import DataCiteSchemaV1
from b2share.modules.records.serializers.schemas.eudatcore import EudatCoreSchema
from .xmlserializer import XMLSerializer

from b2share.modules.records.serializers.schemas.datacite import DataCiteSchemaV1, DataCiteSchemaV2
from b2share.modules.records.serializers.schemas.eudatcore import EudatCoreSchema
from .xmlserializer import XMLSerializer
from .schemas import schema44
from b2share.modules.records.serializers.response import record_responsify, \
    JSONSerializer

json_v1 = JSONSerializer(RecordSchemaJSONV1)
json_v1_response = record_responsify(json_v1, 'application/json')
json_v1_search = search_responsify(json_v1, 'application/json')


# OAI-PMH record serializers.
dc_v1 = DublinCoreSerializer(RecordSchemaDublinCoreV1, replace_refs=True)
marcxml_v1 = MARCXMLSerializer(to_marc21, schema_class=RecordSchemaMarcXMLV1, replace_refs=True)
oaipmh_oai_dc = dc_v1.serialize_oaipmh
oaipmh_marc21_v1 = marcxml_v1.serialize_oaipmh
eudatcore_v1 = XMLSerializer(EudatCoreSchema, replace_refs=True).serialize_oaipmh

# DOI record serializers.
datacite_v31 = DataCite31Serializer(DataCiteSchemaV1, replace_refs=True)
class Datacite44Serializer(BaseDataCiteSerializer):
    schema = schema44
    version = '4.4'

datacite_v44 = Datacite44Serializer(DataCiteSchemaV2, replace_refs=True)
