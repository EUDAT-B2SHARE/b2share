# -*- coding: utf-8 -*-
#
# This file is part of EUDAT B2Share.
# Copyright (C) 2017 CERN.
# Copyright (C) 2023 CSC
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

from invenio_stats.queries import ESTermsQuery, extract_date
from elasticsearch_dsl import Search
from elasticsearch_dsl.connections import connections
from invenio_stats.errors import InvalidRequestInputError
from invenio_search import current_search_client
import six

"""Statistics queries."""

def register_queries():
   return [
       dict(
           query_name='record-views-total',
           query_class=ESTermsQuery,
           query_config=dict(
               index='stats-record-view',
               doc_type='record-view-day-aggregation',
               copy_fields=dict(
                   pid_type='pid_type',
                   pid_value='pid_value',
                   community='community'
               ),
               metric_fields=dict(
                   count=('sum', 'count', {}),
               ),
               required_filters=dict(
                   pid_value='pid_value'
               ),
               aggregated_fields=['pid_value']
           )
       ),
       dict(
           query_name='community-record-views-total',
           query_class=ESDualQuery,
           query_config=dict(
               index_2='stats-record-view',
               #doc_type='record-view-day-aggregation',
               copy_fields=dict(
                   #community='community'
               ),
               metric_fields=dict(
                   total=('sum', 'count', 'field', {}),
               ),
               required_filters=dict(
                   community='community'
               ),
               required_filters_1=dict(
                    community='community'
                ),
               #aggregated_fields=['community']
           )
       ),
        dict(
            query_name='community-file-download-total',
            query_class=ESDualQuery,
            query_config=dict(
                index_1='records',
                index_2='stats-file-download',
                doc_type='file-download-day-aggregation',
                copy_fields=dict(
                    #file_key='file_key'
                ),
                metric_fields=dict(
                    total=('sum', 'count', 'field', {}),
                ),
                required_filters_1=dict(
                    community='community'
                ),
                #aggregated_fields=['file_key']
            )
        ),
        dict(
           query_name='community-file-size-total',
           query_class=ESDualQuery,
           query_config=dict(
               #index_1='records-records',
               index_2='records',
               #doc_type='record-view-day-aggregation',
               copy_fields=dict(
                   #community='community'
               ),
               metric_fields=dict(
                   total=('sum', '_files.size', 'field', {}),
               ),
               required_filters=dict(
                   community='community'
               ),
               required_filters_1=dict(
                   community='community'
               ),
               #aggregated_fields=['community']
           )
       ),
        dict(
           query_name='community-file-amount-total',
           query_class=ESDualQuery,
           query_config=dict(
               #index_1='records-records',
               index_2='records',
               #doc_type='record-view-day-aggregation',
               copy_fields=dict(
                   #length='length'
               ),
               metric_fields=dict(
                   total=('sum', 'return _source._files.size()', 'script', {}),
               ),
               required_filters=dict(
                   community='community'
               ),
               required_filters_1=dict(
                   community='community'
               ),
               #aggregated_fields=['community']
           )
       )]

class ESQuery(object):
    """Elasticsearch query."""

    def __init__(self, query_name, index_2, index_1=None, doc_type=None, metric_fields=None, client=None,
                 *args, **kwargs):
        """Constructor.
        :param doc_type: queried document type.
        :param index_1: queried index for first query.
        :param index_2: queried index for second query.
        :param metric_fields: dict of fields and/or scripts to aggregate metrics.
        :param client: elasticsearch client used to query.
        """
        super(ESQuery, self).__init__()
        self.index_1 = index_1
        self.index_2 = index_2
        self.client = client or current_search_client
        self.query_name = query_name
        self.doc_type = doc_type
        self.metric_fields = metric_fields or {'total': ('sum', 'count', {})}

    def run(self, *args, **kwargs):
        """Run the query."""
        raise NotImplementedError()

class ESDualQuery(ESQuery):
    """
    Elasticsearch Dual query. This can be run in two 'modes': Single query and dual query.
    """

    def __init__(self, time_field='timestamp', copy_fields=None,
                 required_filters=None, required_filters_1=None, aggregated_fields=None, scripts=None,
                 *args, **kwargs):
        """Constructor.
        :param time_field: name of the timestamp field.
        :param copy_fields: list of fields to copy from the top hit document
            into the resulting aggregation item.
        :param required_filters: Dict of "mandatory query parameter" ->
            "filtered field" for the second query.
        :param required_filters_1: Dict of query params for first query.
        :params scripts: Dict of scripts to add to query. These will be added as script_fields
        :param aggregated_fields: List of fields which will be used in the
            terms aggregations.
        """
        super(ESDualQuery, self).__init__(*args, **kwargs)
        self.time_field = time_field
        self.copy_fields = copy_fields or dict()
        self.required_filters = required_filters or {}
        self.required_filters_1 = required_filters_1 or {}
        self.aggregated_fields = aggregated_fields or []
        self.scripts = scripts or {}
        #assert len(self.aggregated_fields) > 0

    def validate_arguments(self, start_date, end_date, **kwargs):
        """Validate query arguments."""
        if kwargs.keys() != self.required_filters_1.keys():
            raise InvalidRequestInputError(
                'Missing one of the required parameters {0} in '
                'query {1}'.format(set(self.required_filters.keys()),
                                   self.query_name)
            )

    def build_query(self, start_date, end_date, buckets=None, **kwargs):
        """Build the elasticsearch query."""
        agg_query = Search(using=self.client,
                           index=self.index_2,
                           doc_type=self.doc_type)
        if start_date is not None or end_date is not None:
            time_range = {}
            if start_date is not None:
                time_range['gte'] = start_date.isoformat()
            if end_date is not None:
                time_range['lte'] = end_date.isoformat()
            agg_query = agg_query.filter(
                'range',
                **{self.time_field: time_range})

        term_agg = agg_query.aggs
        for term in self.aggregated_fields:
            term_agg = term_agg.bucket(term, 'terms', field=term, size=0)

        if self.scripts:
            for script in self.scripts.items():
                agg_query = agg_query.script_fields(**{script[0]: script[1]})

        for dst, (metric, field, type, opts) in self.metric_fields.items():
            if type == 'field':
                term_agg.metric(dst, metric, field=field, **opts)
            if type == 'script':
                term_agg.metric(dst, metric, script=field, **opts)

        if self.copy_fields:
            term_agg.metric(
                'top_hit', 'top_hits', size=1
            )

        for query_param, filtered_field in self.required_filters.items():
            if query_param in kwargs:
                agg_query = agg_query.filter(
                    'term', **{filtered_field: kwargs[query_param]}
                )
        if buckets:
            agg_query = agg_query.filter(
                        'terms', **{'bucket_id': buckets}
                    )

        return agg_query

    def process_query_result(self, result, start_date, end_date, community=None):
        """Build the result using the query result."""
        def build_buckets(agg, fields, res, community=None):
            """Build recursively result buckets."""
            if fields:
                field = fields[0]
                res.update(
                    type='bucket',
                    field=field,
                    key_type='terms',
                    buckets=list(map(
                        lambda sub: build_buckets(sub, fields[1:],
                                                    dict(key=sub['key'])),
                        agg[field]['buckets']))
                )
            else:
                res.update(
                    value=agg['total']['value'],
                    key=agg.get('key', community),
                )
                if self.copy_fields and agg['top_hit']['hits']['hits']:
                    doc = agg['top_hit']['hits']['hits'][0]['_source']
                    for destination, source in self.copy_fields.items():
                        if isinstance(source, six.string_types):
                            res[destination] = doc[source]
                        else:
                            res[destination] = source(
                                res,
                                doc
                            )
            return res

        return build_buckets(result['aggregations'], self.aggregated_fields,
                                dict(), community=community)

    def run(self, start_date=None, end_date=None, **kwargs):
        """Run the query."""
        start_date = extract_date(start_date) if start_date else None
        end_date = extract_date(end_date) if end_date else None
        self.validate_arguments(start_date, end_date, **kwargs)
        buckets = None
        # If we want to get buckets and run a search based on that; get the buckets
        if self.index_1:
            # Size for one elasticsearch query page
            size = 1000
            q1 = Search(using=current_search_client, index=self.index_1)
            q1 = q1.fields(['_files.bucket'])
            
            for query_param, filtered_field in self.required_filters_1.items():
                if query_param in kwargs:
                    q1 = q1.filter(
                        'term', **{filtered_field: kwargs[query_param]}
                    )
            q1 = q1.params(size=size, scroll='1m')
            res1 = q1.execute().to_dict()
            hits = res1.get('hits', {}).get('hits', [])
            buckets = [hit.get('fields', {}).get('_files.bucket', [])[0] for hit in hits if hit.get('fields', None)]
            ind = size
            connection = connections.get_connection(current_search_client)
            # Loop until all pages went through
            while res1.get('hits').get('total') > ind:
                ind += size
                try:
                    loop_res = connection.scroll(scroll_id=res1.get('_scroll_id')) # Might return error with 404, if trying to request page n+1
                except:
                    break
                hits = loop_res.get('hits', {}).get('hits', [])
                loop_buckets = [hit.get('fields', {}).get('_files.bucket', [])[0] for hit in hits if hit.get('fields', None)]
                buckets = [*buckets, *loop_buckets]

        agg_query = self.build_query(start_date, end_date, buckets, **kwargs)
        query_result = agg_query.execute().to_dict()
        res = self.process_query_result(query_result, start_date, end_date, community=kwargs['community'])
        return res
