# -*- coding: utf-8 -*-
# B2SHARE2

from __future__ import absolute_import

from flask import Blueprint, jsonify

from invenio_rest import ContentNegotiatedMethodView


blueprint = Blueprint(
    'b2share_records',
    __name__,
    url_prefix='/xrecords'
)


def community_to_json_serializer(data, code=200, headers=None):
    """Build a json flask response using the given data.
    :Returns: A flask response with json data.
    :Returns Type: :py:class:`flask.Response`
    """
    response = jsonify(data)
    response.status_code = code
    if headers is not None:
        response.headers.extend(headers)
    return response


class RecordList(ContentNegotiatedMethodView):
    view_name = 'record_list'

    def __init__(self, *args, **kwargs):
        super(RecordList, self).__init__(*args, **kwargs)
        self.serializers = {
            'application/json': community_to_json_serializer,
        }

    def get(self, **kwargs):
        """
        Retrieve list of records.
        """
        from .mock_impl import mock_records
        return {'records': mock_records}

    def post(self, **kwargs):
        """
        Creates a new record object (it can be empty or with metadata), owned
        by current user. The default state of record status is 'draft'
        """
        return {}


class Record(ContentNegotiatedMethodView):
    view_name = 'record_item'

    def __init__(self, *args, **kwargs):
        super(Record, self).__init__(*args, **kwargs)
        self.serializers = {
            'application/json': community_to_json_serializer,
        }

    def get(self, record_id, **kwargs):
        """
        Returns the requested record
        """
        return None

    def patch(self, record_id, **kwargs):
        """
        Edits the Record and submit it.
        """
        return None

    def delete(self, record_id, **kwargs):
        """
        Deletes the record:
            - if the state of record is draft: it will be deleted
            - if the state is released: it will be marked as deleted.
                Only available to superadmins
        """
        return None


# ----------------------------------------------- FILES


class FileList(ContentNegotiatedMethodView):
    view_name = 'file_list'

    def __init__(self, *args, **kwargs):
        super(FileList, self).__init__(*args, **kwargs)
        self.serializers = {
            'application/json': community_to_json_serializer,
        }

    def get(self, record_id, **kwargs):
        """
        Retrieve list of files in a record.
        """
        return None

    def post(self, record_id, **kwargs):
        """
        Add a new file to the record. The record state should be 'draft'
        """
        return None


class FileContainer(ContentNegotiatedMethodView):
    view_name = 'file_container'

    def __init__(self, *args, **kwargs):
        super(FileContainer, self).__init__(*args, **kwargs)
        self.serializers = {
            'application/json': community_to_json_serializer,
        }

    def get(self, record_id, file_id, **kwargs):
        """
        Get a file metadata
        """
        return None

    def patch(self, record_id, file_id, **kwargs):
        """
        Rename the file or container
        """
        return None

    def delete(self, record_id, file_id, **kwargs):
        """
        Delete a file/container (only possible for draft records).
        If it is a container it deletes recursively its children.
        """
        return None


class File(ContentNegotiatedMethodView):
    view_name = 'file_item'

    def __init__(self, *args, **kwargs):
        super(File, self).__init__(*args, **kwargs)
        self.serializers = {
            'application/json': community_to_json_serializer,
        }

    def get(self, record_id, file_id, **kwargs):
        """
        Get a file's content
        """
        return None


# ----------------------------------------------- REFERENCES


class RecordReferenceList(ContentNegotiatedMethodView):
    view_name = 'record_reference_list'

    def __init__(self, *args, **kwargs):
        super(RecordReferenceList, self).__init__(*args, **kwargs)
        self.serializers = {
            'application/json': community_to_json_serializer,
        }

    def get(self, record_id, **kwargs):
        """
        Returns the record's references
        """
        return None

    def post(self, record_id, **kwargs):
        """
        Create a new reference
        """
        return None


class RecordReference(ContentNegotiatedMethodView):
    view_name = 'record_reference_item'

    def __init__(self, *args, **kwargs):
        super(RecordReference, self).__init__(*args, **kwargs)
        self.serializers = {
            'application/json': community_to_json_serializer,
        }

    def get(self, record_id, ref_id, **kwargs):
        """
        Returns a Reference with the specified id
        """
        return None

    def delete(self, record_id, ref_id, **kwargs):
        """
        Deletes a reference
        """
        return None


blueprint.add_url_rule('/',
                       view_func=RecordList.as_view(RecordList.view_name))
blueprint.add_url_rule('/<int:record_id>',
                       view_func=Record.as_view(Record.view_name))
blueprint.add_url_rule('/<int:record_id>/files',
                       view_func=FileList.as_view(FileList.view_name))
blueprint.add_url_rule('/<int:record_id>/files/<int:file_id>',
                       view_func=File.as_view(File.view_name))
blueprint.add_url_rule('/<int:record_id>/references',
                       view_func=RecordReferenceList.as_view(RecordReferenceList.view_name))
blueprint.add_url_rule('/<int:record_id>/references/<int:ref_id>',
                       view_func=RecordReference.as_view(RecordReference.view_name))
