# -*- coding: utf-8 -*-

from __future__ import absolute_import

from flask.ext.restful import Resource

# ----------------------------------------------- COMMUNITIES


class CommunityList(Resource):
    def get(self, **kwargs):
        """
        Retrieve list of communities.
        """
        return None

    def post(self, **kwargs):
        """
        Creates a new community that has associated a new metadata fieldset.
        Only administrators can use it.
        parameter: name, description, logo
        """
        return None


class Community(Resource):
    def get(self, community_id, **kwargs):
        """
        Get a community metadata and description.
        """
        return None

    def patch(self, community_id, **kwargs):
        """
        Modify a community
        """
        return None


# ----------------------------------------------- SCHEMA


class SchemaList(Resource):
    def get(self, **kwargs):
        """
        Retrieve list of schemas.
        """
        return None

    def post(self, **kwargs):
        """
        Create a new schema
        """
        return None


class Schema(Resource):
    def get(self, schema_id, **kwargs):
        """
        Get a schema
        """
        return None

    def post(self, schema_id, **kwargs):
        """
        Create a new schema from an old one. It might be a new version.
        """
        return None


# ----------------------------------------------- RECORDS


class RecordList(Resource):
    def get(self, **kwargs):
        """
        Retrieve list of records.
        """
        return None

    def post(self, **kwargs):
        """
        Creates a new record object (it can be empty or with metadata), owned
        by current user. The default state of record status is 'draft'
        """
        return None


class Record(Resource):
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


class FileList(Resource):
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


class FileContainer(Resource):
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


class File(Resource):
    def get(self, record_id, file_id, **kwargs):
        """
        Get a file's content
        """
        return None


# ----------------------------------------------- REFERENCES


class RecordReferenceList(Resource):
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


class RecordReference(Resource):
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


# ----------------------------------------------- USERS


class UserList(Resource):
    def get(self, **kwargs):
        """
        Search for users.
        """
        return None


class User(Resource):
    def get(self, user_id, **kwargs):
        """
        Get a user profile information
        """
        return None


def setup_app(app, api):
    api.add_resource(CommunityList, '/api/communities')
    api.add_resource(Community, '/api/communities/<int:community_id>')
    api.add_resource(SchemaList, '/api/schemas')
    api.add_resource(Schema, '/api/schemas/<int:schema_id>')
    api.add_resource(RecordList, '/api/records')
    api.add_resource(Record, '/api/records/<int:record_id>')
    api.add_resource(FileList, '/api/records/<int:record_id>/files')
    api.add_resource(FileContainer, '/api/records/<int:record_id>/files/<int:file_id>')
    api.add_resource(File, '/api/records/<record_id>/files/<file_id>/content')
    api.add_resource(RecordReferenceList, '/api/records/<int:record_id>/references')
    api.add_resource(RecordReference, '/api/records/<int:record_id>/references/<int:ref_id>')
    api.add_resource(UserList, '/api/users')
    api.add_resource(User, '/api/users/<int:user_id>')
