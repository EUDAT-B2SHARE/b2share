
import json
from copy import deepcopy
from functools import partial

from flask import Blueprint, abort, make_response, request, url_for
from werkzeug.utils import secure_filename
from invenio_db import db
from invenio_files_rest.errors import InvalidOperationError
from invenio_oauth2server import require_api_auth, require_oauth_scopes
from invenio_pidstore.errors import PIDInvalidAction
from invenio_pidstore.resolver import Resolver
from invenio_records_rest.utils import obj_or_import_string
from invenio_records_rest.views import need_record_permission, pass_record
from invenio_rest import ContentNegotiatedMethodView
from invenio_rest.views import create_api_errorhandler
from webargs import fields
from webargs.flaskparser import use_kwargs
from flask import Blueprint, current_app, jsonify, url_for
from invenio_rest.views import ContentNegotiatedMethodView
from b2share.modules.schemas.views import pass_community_schema
from b2share.modules.schemas.serializers import \
    community_schema_json_schema_link
from werkzeug.local import LocalProxy
from invenio_records_rest.views import RecordsListResource
from invenio_records_rest.links import default_links_factory
from invenio_records.api import Record
from invenio_records_rest.views import RecordResource
from invenio_deposit.views.rest import DepositActionResource
from invenio_deposit.search import DepositSearch
from invenio_deposit.api import Deposit as InvenioDeposit

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
    read_permission_factory = obj_or_import_string(
        read_permission_factory_imp
    )
    create_permission_factory = obj_or_import_string(
        create_permission_factory_imp
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
        record_class, default=Record
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

    item_view = RecordResource.as_view(
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
        options = deepcopy(options)

        # if 'files_serializers' in options:
        #     files_serializers = options.get('files_serializers')
        #     files_serializers = {mime: obj_or_import_string(func)
        #                          for mime, func in files_serializers.items()}
        #     del options['files_serializers']
        # else:
        #     files_serializers = {}

        if 'record_serializers' in options:
            serializers = options.get('record_serializers')
            serializers = {mime: obj_or_import_string(func)
                           for mime, func in serializers.items()}
        else:
            serializers = {}

        # file_list_route = options.pop(
        #     'file_list_route',
        #     '{0}/files'.format(options['item_route'])
        # )
        # file_item_route = options.pop(
        #     'file_item_route',
        #     '{0}/files/<path:key>'.format(options['item_route'])
        # )

        for rule in records_rest_url_rules(endpoint, **options):
            blueprint.add_url_rule(**rule)

        search_class = obj_or_import_string(
            options['search_class'], default=DepositSearch
        )
        record_class = obj_or_import_string(
            options['record_class'], default=InvenioDeposit
        )

        search_class_kwargs = {}
        if options.get('search_index'):
            search_class_kwargs['index'] = options['search_index']

        if options.get('search_type'):
            search_class_kwargs['doc_type'] = options['search_type']

        ctx = dict(
            read_permission_factory=obj_or_import_string(
                options.get('read_permission_factory_imp')
            ),
            create_permission_factory=obj_or_import_string(
                options.get('create_permission_factory_imp')
            ),
            update_permission_factory=obj_or_import_string(
                options.get('update_permission_factory_imp')
            ),
            delete_permission_factory=obj_or_import_string(
                options.get('delete_permission_factory_imp')
            ),
            search_class=partial(search_class, **search_class_kwargs),
            default_media_type=options.get('default_media_type'),
            record_class=record_class,
        )

        deposit_actions = DepositActionResource.as_view(
            DepositActionResource.view_name.format(endpoint),
            serializers=serializers,
            pid_type=options['pid_type'],
            ctx=ctx,
        )

        blueprint.add_url_rule(
            '{0}/actions/<any(publish,edit,discard):action>'.format(
                options['item_route']
            ),
            view_func=deposit_actions,
            methods=['POST'],
        )


        # deposit_files = DepositFilesResource.as_view(
        #     DepositFilesResource.view_name.format(endpoint),
        #     serializers=files_serializers,
        #     pid_type=options['pid_type'],
        #     ctx=ctx,
        # )

        # blueprint.add_url_rule(
        #     file_list_route,
        #     view_func=deposit_files,
        #     methods=['GET', 'POST', 'PUT'],
        # )

        # deposit_file = DepositFileResource.as_view(
        #     DepositFileResource.view_name.format(endpoint),
        #     serializers=files_serializers,
        #     pid_type=options['pid_type'],
        #     ctx=ctx,
        # )

        # blueprint.add_url_rule(
        #     file_item_route,
        #     view_func=deposit_file,
        #     methods=['GET', 'PUT', 'DELETE'],
        # )
    blueprint.add_url_rule(
        '/communities/<string:community_id>/schemas/<string:schema_version_nb>/deposit',
        view_func=CommunityDepositSchemaResource.as_view(
            CommunityDepositSchemaResource.view_name,
        ),
        methods=['GET'],
    )
    return blueprint

def community_deposit_schema_to_json_serializer(deposit_schema, code=200,
                                                headers=None):
    response = jsonify(deposit_schema_to_dict(deposit_schema))
    response.status_code = code
    response.set_etag(
        str(deposit_schema.community_schema.released.utcfromtimestamp(0)))
    if headers is not None:
        response.headers.extend(headers)
    return response

def deposit_schema_to_dict(deposit_schema):
    return dict(
        json_schema=deposit_schema.json_schema,
        links={
            'self': '{}#/json_schema'.format(url_for(
            'b2share_deposit_rest.community_deposit_schema',
            community_id=deposit_schema.community_schema.community,
            schema_version_nb=deposit_schema.community_schema.version,
            _external=True))
        }
    )

class CommunityDepositSchema(object):
    def __init__(self, community_schema):
        self.community_schema = community_schema

    @property
    def json_schema(self):
        return {
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'title': 'B2Share Deposit schema',
            'allOf': [{
                '$ref':
                community_schema_json_schema_link(self.community_schema)
            }, {
                '$ref':
                current_jsonschemas.path_to_url(
                    'deposits/deposit-v1.0.0.json')
            }]
        }
class CommunityDepositSchemaResource(ContentNegotiatedMethodView):
    view_name = 'community_deposit_schema'

    def __init__(self, **kwargs):
        """Constructor."""
        super(CommunityDepositSchemaResource, self).__init__(
            serializers={
                'application/json':
                community_deposit_schema_to_json_serializer,
            },
            default_method_media_type={
                'GET': 'application/json',
            },
            default_media_type='application/json',
            **kwargs
        )
    @pass_community_schema
    def get(self, community_schema, *args, **kwargs):
        return CommunityDepositSchema(community_schema)

# blueprint.add_url_rule(
#     '/communities/<string:community_id>/schemas/<string:schema_version_nb>/deposit',
#     view_func=CommunityDepositSchemaResource.as_view(record
#         CommunityDepositSchemaResource.view_name,
#     ),
#     methods=['GET'],
# )
