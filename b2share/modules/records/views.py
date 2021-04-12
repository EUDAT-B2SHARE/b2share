# -*- coding: utf-8 -*-
#
# This file is part of EUDAT B2Share.
# Copyright (C) 2016 CERN.
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


import uuid
import re
from functools import partial, wraps

from sqlalchemy import and_
from sqlalchemy.orm import aliased
from flask import Blueprint, abort, request, url_for, make_response
from flask import jsonify, Flask, current_app
from invenio_db import db
from invenio_pidstore.resolver import Resolver
from invenio_pidstore.errors import PIDDoesNotExistError, PIDRedirectedError
from invenio_pidstore.models import PersistentIdentifier
from invenio_pidrelations.contrib.versioning import PIDVersioning
from invenio_pidrelations.models import PIDRelation
from invenio_records_files.api import Record
from invenio_rest.errors import RESTValidationError
from invenio_search import RecordsSearch
from jsonschema.exceptions import ValidationError
from invenio_records.models import RecordMetadata
from invenio_records_files.api import RecordsBuckets
from invenio_records_rest.views import (pass_record,
                                        RecordsListResource, RecordResource,
                                        RecordsListOptionsResource,
                                        SuggestResource)
from invenio_records_rest.links import default_links_factory
from invenio_records_rest.query import default_search_factory
from invenio_records_rest.utils import obj_or_import_string
from invenio_mail.tasks import send_email
from invenio_rest import ContentNegotiatedMethodView
from invenio_accounts.models import User

from b2share.modules.records.providers import RecordUUIDProvider
from b2share.modules.deposit.serializers import json_v1_response as \
    deposit_serializer
from b2share.modules.deposit.errors import RecordNotFoundVersioningError, \
    IncorrectRecordVersioningError


# duplicated from invenio-records-rest because we need
# to pass the previous version record data
def verify_record_permission(permission_factory, record, **kwargs):
    """Check that the current user has the required permissions on record.
    In case the permission check fails, an Flask abort is launched.
    If the user was previously logged-in, a HTTP error 403 is returned.
    Otherwise, is returned a HTTP error 401.
    :param permission_factory: permission factory used to check permissions.
    :param record: record whose access is limited.
    """
    # Note, cannot be done in one line due overloading of boolean
    # operations permission object.
    if not permission_factory(record=record, **kwargs).can():
        from flask_login import current_user
        if not current_user.is_authenticated:
            abort(401)
        abort(403)


def create_blueprint(endpoints):
    """Create Invenio-Records-REST blueprint."""
    blueprint = Blueprint(
        'b2share_records_rest',
        __name__,
        url_prefix='',
    )

    for endpoint, options in (endpoints or {}).items():
        for rule in create_url_rules(endpoint, **options):
            blueprint.add_url_rule(**rule)

    # catch record validation errors
    @blueprint.errorhandler(ValidationError)
    def validation_error(error):
        """Catch validation errors."""
        return RESTValidationError().get_response()

    return blueprint


def create_url_rules(endpoint, list_route=None, item_route=None,
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
                     suggesters=None):
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
    search_class = obj_or_import_string(
        search_class, default=RecordsSearch
    )

    search_class_kwargs = {}
    if search_index:
        search_class_kwargs['index'] = search_index
    else:
        search_index = search_class.Meta.index

    if search_type:
        search_class_kwargs['doc_type'] = search_type
    else:
        search_type = search_class.Meta.doc_types

    if search_class_kwargs:
        search_class = partial(search_class, **search_class_kwargs)

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

    # import deposit here in order to avoid dependency loop
    from b2share.modules.deposit.api import Deposit

    list_view = B2ShareRecordsListResource.as_view(
        B2ShareRecordsListResource.view_name.format(endpoint),
        resolver=resolver,
        minter_name=pid_minter,
        pid_type=pid_type,
        pid_fetcher=pid_fetcher,
        read_permission_factory=read_permission_factory,
        create_permission_factory=create_permission_factory,
        # replace the record serializer with deposit serializer as it
        # is used only when the deposit is created.
        record_serializers={
            'application/json': deposit_serializer
        },
        record_loaders=record_loaders,
        search_serializers=search_serializers,
        search_class=search_class,
        default_media_type=default_media_type,
        max_result_window=max_result_window,
        search_factory=(obj_or_import_string(
            search_factory_imp, default=default_search_factory
        )),
        item_links_factory=links_factory,
        record_class=Deposit,
    )
    item_view = B2ShareRecordResource.as_view(
        B2ShareRecordResource.view_name.format(endpoint),
        resolver=resolver,
        read_permission_factory=read_permission_factory,
        update_permission_factory=update_permission_factory,
        delete_permission_factory=delete_permission_factory,
        serializers=record_serializers,
        loaders=record_loaders,
        search_class=search_class,
        links_factory=links_factory,
        default_media_type=default_media_type)

    versions_view = RecordsVersionsResource.as_view(
        RecordsVersionsResource.view_name.format(endpoint),
        resolver=resolver)

    abuse_view = RecordsAbuseResource.as_view(
        RecordsAbuseResource.view_name.format(endpoint),
        resolver=resolver)

    access_view = RequestAccessResource.as_view(
        RequestAccessResource.view_name.format(endpoint),
        resolver=resolver)

    views = [
        dict(rule=list_route, view_func=list_view),
        dict(rule=item_route, view_func=item_view),
        dict(rule=item_route + '/abuse', view_func=abuse_view),
        dict(rule=item_route + '/accessrequests', view_func=access_view),
        # Special case for versioning as the parent PID is redirected.
        dict(rule='/records/<pid_value>/versions', view_func=versions_view),
    ]

    if suggesters:
        suggest_view = SuggestResource.as_view(
            SuggestResource.view_name.format(endpoint),
            suggesters=suggesters,
            search_class=search_class,
        )

        views.append(dict(
            rule=list_route + '_suggest',
            view_func=suggest_view
        ))

    if use_options_view:
        options_view = RecordsListOptionsResource.as_view(
            RecordsListOptionsResource.view_name.format(endpoint),
            search_index=search_index,
            max_result_window=max_result_window,
            default_media_type=default_media_type,
            search_media_types=search_serializers.keys(),
            item_media_types=record_serializers.keys(),
        )
        return [
            dict(rule="{0}_options".format(list_route), view_func=options_view)
        ] + views
    return views


class B2ShareRecordsListResource(RecordsListResource):
    """B2Share resource for records listing and deposit creation."""

    def __init__(self, resolver=None, **kwargs):
        """Constructor."""
        super(B2ShareRecordsListResource, self).__init__(**kwargs)
        self.resolver = resolver

    def post(self, **kwargs):
        """Create a record.

        :returns: The created record.
        """
        # import deposit dependencies here in order to avoid recursive imports
        from b2share.modules.deposit.links import deposit_links_factory
        from b2share.modules.records.api import B2ShareRecord
        from b2share.modules.deposit.api import copy_data_from_previous

        if request.content_type not in self.loaders:
            abort(415)
        version_of = request.args.get('version_of')
        previous_record = None
        data = None
        if version_of:
            try:
                _, previous_record = Resolver(
                    pid_type='b2rec',
                    object_type='rec',
                    getter=B2ShareRecord.get_record,
                ).resolve(version_of)
            # if the pid doesn't exist
            except PIDDoesNotExistError as e:
                raise RecordNotFoundVersioningError()
            # if it is the parent pid
            except PIDRedirectedError as e:
                raise IncorrectRecordVersioningError(version_of)
            # Copy the metadata from a previous version if this version is
            # specified and no data was provided.
            # invenio-records-rest changed missing content_length from 0 to None
            if not request.content_length:
                data = copy_data_from_previous(previous_record.model.json)

        if data is None:
            data = self.loaders[request.content_type]()

        if data is None:
            abort(400)

        # Check permissions
        permission_factory = self.create_permission_factory
        if permission_factory:
            verify_record_permission(permission_factory, data,
                                     previous_record=previous_record)

        # Create uuid for record
        record_uuid = uuid.uuid4().hex
        # Create persistent identifier
        pid = self.minter(record_uuid, data=data)

        # Create record
        record = self.record_class.create(data, id_=record_uuid,
                                          version_of=version_of)
        db.session.commit()

        response = self.make_response(
            pid, record, 201, links_factory=deposit_links_factory)

        # Add location headers
        endpoint = 'b2share_deposit_rest.{0}_item'.format(pid.pid_type)
        location = url_for(endpoint, pid_value=pid.pid_value, _external=True)
        response.headers.extend(dict(location=location))
        return response


class B2ShareRecordResource(RecordResource):
    """B2Share resource for records."""

    def __init__(self, resolver=None, **kwargs):
        """Constructor."""
        super(B2ShareRecordResource, self).__init__(**kwargs)
        self.resolver = resolver

    def put(self, **kwargs):
        """Disable PUT."""
        abort(405)

    @pass_record
    def delete(self, pid, record, *args, **kwargs):
        """Delete a record."""
        self.check_etag(str(record.model.version_id))
        pid_value = request.view_args['pid_value']
        pid, record = pid_value.data

        # Check permissions.
        permission_factory = self.delete_permission_factory
        if permission_factory:
            verify_record_permission(permission_factory, record)
        record.delete()
        db.session.commit()
        return '', 204


class RecordsVersionsResource(ContentNegotiatedMethodView):

    view_name = '{0}_versions'

    def __init__(self, resolver=None, **kwargs):
        """Constructor.

        :param resolver: Persistent identifier resolver instance.
        """
 
        default_media_type = 'application/json'
        super(RecordsVersionsResource, self).__init__(
            serializers={
                'application/json': lambda response: jsonify(response)
            },
            default_method_media_type={
                'GET': default_media_type,
            },
            default_media_type=default_media_type,
            **kwargs)
        self.resolver = resolver

    def get(self, pid=None, **kwargs):
        """GET a list of record's versions."""
        record_endpoint = 'b2share_records_rest.{0}_item'.format(
            RecordUUIDProvider.pid_type)
        pid_value = request.view_args['pid_value']
        pid = RecordUUIDProvider.get(pid_value).pid
        pid_versioning = PIDVersioning(child=pid)
        if pid_versioning.is_child:
            # This is a record PID. Retrieve the parent versioning PID.
            version_parent_pid_value = pid_versioning.parent.pid_value
        else:
            # This is a parent versioning PID
            version_parent_pid_value = pid_value
        records = []
        child_pid_table = aliased(PersistentIdentifier)
        parent_pid_table = aliased(PersistentIdentifier)
        pids_and_meta = db.session.query(
            child_pid_table, RecordMetadata
        ).join(
            PIDRelation,
            PIDRelation.child_id == child_pid_table.id,
        ).join(
            parent_pid_table,
            PIDRelation.parent_id == parent_pid_table.id
        ).filter(
            parent_pid_table.pid_value == version_parent_pid_value,
            RecordMetadata.id == child_pid_table.object_uuid,
        ).order_by(RecordMetadata.created).all()
        for version_number, rec_pid_and_rec_meta in enumerate(pids_and_meta):
            rec_pid, rec_meta = rec_pid_and_rec_meta
            records.append({
                'version': version_number + 1,
                'id': str(rec_pid.pid_value),
                'url': url_for(record_endpoint,
                               pid_value=str(rec_pid.pid_value),
                               _external=True),
                'created': rec_meta.created,
                'updated': rec_meta.updated,
            })
        return {'versions': records}


class RecordsAbuseResource(ContentNegotiatedMethodView):

    view_name = '{0}_abuse'

    def __init__(self, resolver=None, **kwargs):
        """Constructor.

        :param resolver: Persistent identifier resolver instance.
        """
        default_media_type = 'application/json'
        super(RecordsAbuseResource, self).__init__(
            serializers={
                'application/json': lambda response: jsonify(response)
            },
            default_method_media_type={
                'POST': default_media_type,
            },
            default_media_type=default_media_type,
            **kwargs)
        self.resolver = resolver

    def post(self, **kwargs):
        for v in ['abusecontent', 'message', 'email', 'copyright', 'zipcode',
                  'phone', 'illegalcontent', 'city', 'noresearch', 'name',
                  'affiliation', 'address', 'country']:
            if v not in request.json:
                response = jsonify({'Error': '{} is required'.format(v)})
                response.status_code = 400
                return response

        reason_list = ['noresearch', 'abusecontent', 'copyright', 'illegalcontent']
        count = 0
        for ii in reason_list:
            if request.json[ii]:
                count += 1
        if count != 1:
            response = jsonify({
                'Error': 'From \'noresearch\', \'abusecontent\', \'copyright\','
                         ' \'illegalcontent\' (only) one should be True'
            })
            response.status_code = 400
            return response

        friendly = {'abusecontent': 'Abuse or Inappropriate content',
                    'copyright': 'Copyrighted material',
                    'noresearch': 'No research data',
                    'illegalcontent': 'Illegal content'}
        reason = [friendly[ii] for ii in reason_list if request.json[ii]][0]
        msg_content = """
            We have received new abuse report!
            Link: """ + re.sub(r'/abuse\?$', '', request.full_path) + """
            Subject: " Abuse Report for a Record "
            Reason: """ + reason + """
            Message: """ + str(request.json['message']) + """
            Full Name: """ + str(request.json['name']) + """
            Affiliation: """ + str(request.json['affiliation']) + """
            Email: """ + str(request.json['email']) + """
            Address: """ + str(request.json['address']) + """
            City: """ + str(request.json['city']) + """
            Country: """ + str(request.json['country']) + """
            Postal Code: """ + str(request.json['zipcode']) + """
            Phone: """ + str(request.json['phone']) + """
            """
        support = str(current_app.config.get('SUPPORT_EMAIL'))
        send_email(dict(
            subject="Abuse Report for a Record",
            sender=str(request.json['email']),
            recipients=[support],
            body=msg_content,
        ))
        return self.make_response({
            'message':'The record is reported.'
        })


class RequestAccessResource(ContentNegotiatedMethodView):

    view_name = '{0}_accessrequests'

    def __init__(self, resolver=None, **kwargs):
        """Constructor.

        :param resolver: Persistent identifier resolver instance.
        """
        default_media_type = 'application/json'
        super(RequestAccessResource, self).__init__(
            serializers={
                'application/json': lambda response: jsonify(response)
            },
            default_method_media_type={
                'POST': default_media_type,
            },
            default_media_type=default_media_type,
            **kwargs)
        self.resolver = resolver

    @pass_record
    def post(self, pid, record, **kwargs):
        for v in ['message', 'email', 'zipcode', 'phone', 'city', 'name',
                  'affiliation', 'address', 'country']:
            if v not in request.json:
                response = jsonify({'Error': v + ' is required'})
                response.status_code = 400
                return response
        msg_content = """
            You have a request for your data!
            Link: """ + re.sub(r'/abuserecords\?$', '', request.full_path) + """
            Subject: " Request Access to Data Files "
            Message: """ + str(request.json['message']) + """
            Full Name: """ + str(request.json['name']) + """
            Affiliation: """ + str(request.json['affiliation']) + """
            Email: """ + str(request.json['email']) + """
            Address: """ + str(request.json['address']) + """
            City: """ + str(request.json['city']) + """
            Country: """ + str(request.json['country']) + """
            Postal Code: """ + str(request.json['zipcode']) + """
            Phone: """ + str(request.json['phone']) + """
            """
        if 'contact_email' in record:
            recipients = [record['contact_email']]
        else:
            owners = User.query.filter(
                User.id.in_(record['_deposit']['owners'])).all()
            recipients = [owner.email for owner in owners]
        send_email(dict(
            subject="Request Access to Data Files",
            sender=str(request.json['email']),
            recipients=recipients,
            body=msg_content,
        ))
        return self.make_response({
            'message': 'An email was sent to the record owner.'
        })
