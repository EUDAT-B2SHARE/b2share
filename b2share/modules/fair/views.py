# -*- coding: utf-8 -*-
#
# This file is part of EUDAT B2Share.
# Copyright (C) 2015, 2016, University of Tuebingen, CERN.
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

"""EUDAT B2ACCESS Fair REST API."""

import json
from flask import Blueprint
from pyld import jsonld
from invenio_pidstore.models import PersistentIdentifier
from invenio_records import Record
from invenio_rest import ContentNegotiatedMethodView

from invenio_records_rest.serializers.jsonld import JSONLDSerializer
from .contexts import CONTEXT, _TestSchema


blueprint = Blueprint(
    'fdp',
    __name__,
)


class FairDataPoint(ContentNegotiatedMethodView):
    view_name = 'fair_data_point'

    def __init__(self, **kwargs):
        """Constructor."""
        super(FairDataPoint, self).__init__(
            serializers={
                'application/ld-json':
                    # This is a record specific serializer for json-ld
                    JSONLDSerializer(CONTEXT, schema_class=_TestSchema).
                    serialize
            },
            default_method_media_type={
                'GET': 'application/ld-json',
                'PATCH': 'application/ld-json',
            },
            default_media_type='application/ld-json',
            **kwargs
        )

    def get(self):
        return (PersistentIdentifier(pid_type='recid', pid_value='2'),
                Record({'title': 'mytitle', 'recid': '2'}))

    def patch(self):
        pass


class CatalogMetadata(ContentNegotiatedMethodView):
    view_name = 'catalog_metadata'

    def __init__(self, **kwargs):
        """Constructor."""
        super(CatalogMetadata, self).__init__(
            serializers={
                'application/ld-json':
                    # This is a simpler generic serializer with
                    # the work to create the json-ld happening
                    # inside the get method
                    json.dumps
            },
            default_method_media_type={
                'GET': 'application/ld-json',
                'POST': 'application/ld-json',
            },
            default_media_type='application/ld-json',
            **kwargs
        )

    def get(self, catalog_id):
        doc = {
            "http://schema.org/name": "Manu Sporny",
            "http://schema.org/url": {"@id": "http://manu.sporny.org/"},
            "http://schema.org/image": {"@id": "http://manu.sporny.org/images/manu.png"}
        }

        context = {
            "name": "http://schema.org/name",
            "homepage": {"@id": "http://schema.org/url", "@type": "@id"},
            "image": {"@id": "http://schema.org/image", "@type": "@id"}
        }

        compacted = jsonld.compact(doc, context)
        return compacted

    def post(self, catalog_id):
        pass


class DatasetMetadata(ContentNegotiatedMethodView):
    view_name = 'dataset_metadata'

    def __init__(self, **kwargs):
        """Constructor."""
        super(DatasetMetadata, self).__init__(
            serializers={
                'application/ld-json':
                    JSONLDSerializer(CONTEXT, schema_class=_TestSchema).
                    serialize
            },
            default_method_media_type={
                'GET': 'application/ld-json',
                'POST': 'application/ld-json',
            },
            default_media_type='application/ld-json',
            **kwargs
        )

    def get(self, catalog_id, dataset_id):
        pass

    def post(self, catalog_id, dataset_id):
        pass


class DistributionMetadata(ContentNegotiatedMethodView):
    view_name = 'distribution_metadata'

    def __init__(self, **kwargs):
        """Constructor."""
        super(DistributionMetadata, self).__init__(
            serializers={
                'application/ld-json':
                    JSONLDSerializer(CONTEXT, schema_class=_TestSchema).
                    serialize
            },
            default_method_media_type={
                'GET': 'application/ld-json',
                'POST': 'application/ld-json',
            },
            default_media_type='application/ld-json',
            **kwargs
        )

    def get(self, catalog_id, dataset_id, distribution_id):
        pass

    def post(self, catalog_id, dataset_id, distribution_id):
        pass


blueprint.add_url_rule('/fdp/',
                       view_func=FairDataPoint.as_view(
                           FairDataPoint.view_name))
blueprint.add_url_rule('/fdp/<catalog_id>',
                       view_func=CatalogMetadata.as_view(
                           CatalogMetadata.view_name))
blueprint.add_url_rule('/fdp/<catalog_id>/<dataset_id>',
                       view_func=DatasetMetadata.as_view(
                           DatasetMetadata.view_name))
blueprint.add_url_rule('/fdp/<catalog_id>/<dataset_id>/<distribution_id>',
                       view_func=DistributionMetadata.as_view(
                           DistributionMetadata.view_name))
