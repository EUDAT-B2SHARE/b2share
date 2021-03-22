# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016 CERN.
#
# Invenio is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

from functools import partial

from flask import abort, Blueprint, current_app, g, request
from invenio_files_rest.errors import InvalidOperationError
from invenio_pidstore.errors import PIDInvalidAction
from invenio_pidstore.resolver import Resolver
from invenio_db import db
from invenio_records_rest.utils import obj_or_import_string
from invenio_rest.views import create_api_errorhandler
from werkzeug.local import LocalProxy
from invenio_records_rest.links import default_links_factory
from invenio_records_rest.views import RecordResource, pass_record
from invenio_records_rest.views import verify_record_permission
from invenio_deposit.search import DepositSearch
from invenio_indexer.api import RecordIndexer
from invenio_pidrelations.contrib.versioning import PIDVersioning
from invenio_pidstore.models import PIDStatus
from b2share.modules.deposit.api import Deposit
from b2share.modules.records.providers import RecordUUIDProvider


current_jsonschemas = LocalProxy(
    lambda: current_app.extensions['invenio-jsonschemas']
)


def records_rest_url_rules(endpoint, list_route=None, item_route=None,
                           pid_type=None, pid_minter=None, pid_fetcher=None,
                           read_permission_factory_imp=None,
                           create_permission_factory_imp=None,
                           update_permission_factory_imp=None,
                           delete_permission_factory_imp=None,
                           record_class=None,
                           record_serializers=None,
                           record_loaders=None,
                           search_class=None,
                           search_serializers=None,
                           search_index=None, search_type=None,
                           default_media_type=None,
                           max_result_window=None, use_options_view=True,
                           search_factory_imp=None, links_factory_imp=None,
                           suggesters=None, **kwargs):
    """Create Werkzeug URL rules.

    :param endpoint: Name of endpoint.
    :param list_route: record listing URL route . Required.
    :param item_route: record URL route (must include ``<pid_value>`` pattern).
        Required.
    :param pid_type: Persistent identifier type for endpoint. Required.
    :param template: Template to render. Defaults to
        ``invenio_records_ui/detail.html``.
    :param read_permission_factory_imp: Import path to factory that creates a
        read permission object for a given record.
    :param create_permission_factory_imp: Import path to factory that creates a
        create permission object for a given record.
    :param update_permission_factory_imp: Import path to factory that creates a
        update permission object for a given record.
    :param delete_permission_factory_imp: Import path to factory that creates a
        delete permission object for a given record.
    :param search_index: Name of the search index used when searching records.
    :param search_type: Name of the search type used when searching records.
    :param record_class: Name of the record API class.
    :param record_serializers: serializers used for records.
    :param search_serializers: serializers used for search results.
    :param default_media_type: default media type for both records and search.
    :param max_result_window: maximum number of results that Elasticsearch can
        provide for the given search index without use of scroll. This value
        should correspond to Elasticsearch ``index.max_result_window`` value
        for the index.
    :param use_options_view: Determines if a special option view should be
        installed.

    :returns: a list of dictionaries with can each be passed as keywords
        arguments to ``Blueprint.add_url_rule``.
    """
    from b2share.modules.deposit.api import Deposit

    read_permission_factory = obj_or_import_string(
        read_permission_factory_imp
    )
    update_permission_factory = obj_or_import_string(
        update_permission_factory_imp
    )
    delete_permission_factory = obj_or_import_string(
        delete_permission_factory_imp
    )
    links_factory = obj_or_import_string(
        links_factory_imp, default=default_links_factory
    )
    record_class = obj_or_import_string(
        record_class, default=Deposit
    )
    search_class = obj_or_import_string(
        search_class, default=DepositSearch
    )

    if record_loaders:
        record_loaders = {mime: obj_or_import_string(func)
                          for mime, func in record_loaders.items()}
    record_serializers = {mime: obj_or_import_string(func)
                          for mime, func in record_serializers.items()}
    search_serializers = {mime: obj_or_import_string(func)
                          for mime, func in search_serializers.items()}

    resolver = Resolver(pid_type=pid_type, object_type='rec',
                        getter=partial(record_class.get_record,
                                       with_deleted=True))

    item_view = DepositResource.as_view(
        RecordResource.view_name.format(endpoint),
        resolver=resolver,
        read_permission_factory=read_permission_factory,
        update_permission_factory=update_permission_factory,
        delete_permission_factory=delete_permission_factory,
        serializers=record_serializers,
        loaders=record_loaders,
        search_class=search_class,
        links_factory=links_factory,
        default_media_type=default_media_type)

    return [
        dict(rule=item_route, view_func=item_view),
    ]


def create_blueprint(endpoints):
    """Create Invenio-Deposit-REST blueprint."""
    blueprint = Blueprint(
        'b2share_deposit_rest',
        __name__,
        url_prefix='',
    )
    blueprint.errorhandler(PIDInvalidAction)(create_api_errorhandler(
        status=403, message='Invalid action'
    ))
    blueprint.errorhandler(InvalidOperationError)(create_api_errorhandler(
        status=403, message='Invalid operation'
    ))

    for endpoint, options in (endpoints or {}).items():
        for rule in records_rest_url_rules(endpoint, **options):
            blueprint.add_url_rule(**rule)

    return blueprint


class DepositResource(RecordResource):
    """Resource for deposit items."""

    def __init__(self, resolver=None, **kwargs):
        super(DepositResource, self).__init__(**kwargs)
        self.resolver = resolver

    def patch(self, *args, **kwargs):
        """PATCH the deposit."""
        pid, record = request.view_args['pid_value'].data
        result = super(DepositResource, self).patch(*args, **kwargs)
        record = Deposit.get_record(record['_deposit']['id'])
        self._index_record(record)
        return result

    def put(self, *args, **kwargs):
        """PUT the deposit."""
        abort(405)

    def _index_record(self, record):
        """Index the published record if the deposit is published."""
        if g.deposit_action == 'publish':
            _, published_record = record.fetch_published()
            RecordIndexer().index(published_record)
