# -*- coding: utf-8 -*-
# B2SHARE2.api.py

from __future__ import absolute_import

# The current user is implicitly used throughout the API
# from flask.login import current_user

# TODO:
#   - flat list of files? with pagination?
#   - versioning of community, schema, records:
#       - schemas change to new schemas with new ids
#       - deprecate a schema in favour of a new one
#   - ACL and POLICY definitions



###############################################################################

class UserRegistry:
    @staticmethod
    def create_user(nickname, email, full_name, other_info):
        """ Returns a newly created user object, or raises exception."""
        pass

    @staticmethod
    def get_by_id(user_id):
        """Returns a User object or nil"""
        pass

    @staticmethod
    def get_by_name(nickname):
        """ Returns a User object or nil. A nickname uniquely identifies
            one user"""
        pass

    @staticmethod
    def search(part_of_nickname_or_full_name):
        """ Returns a short list of user objects (potential matches)."""
        pass


#from invenio.modules.accounts.models import User as InvenioUser

class User:
    def login(self):
        """ Logs in this user (self), making it the flask current_user
            Raises exception on failure"""
        pass

    def get_info(self, show_private_info=False):
        """ Returns a dict with the user's public info (id, nickname)"""
        pass

    def get_private_info(self, show_private_info=False):
        """ Returns a dict with the user's private info (email, ???)
            or raises AccessDenied exception"""
        pass


###############################################################################

class CommunityRegistry:
    @staticmethod
    def get_by_id(community_id):
        """Returns a Community object or nil"""
        pass

    @staticmethod
    def get_by_name(community_name):
        """Returns a Community object or nil"""
        pass

    @staticmethod
    def create_community(name, description, logo):
        """ Returns a newly created community object or raises exception.
            Only administrators can call this function. A new community
            is implicitly associated with a new, empty, schema list. """
        pass

class Community:
    def get_description(self):
        """ Returns a dict describing the user community. Any media objects
            must be referred to by URL (relative or absolute) """
        # example:
        return {
            "id": 123,
            "name": "MyCommunity",
            "description": "MyCommunity is concerned with the study "\
                "of the newly discovered heptaquark particle",
            "logo": "assets/communities/mycommunity/logo.png"
        }

    def patch_description(self, patch_dict):
        """ Changes the community description with dict. The community id cannot be changed. Only community administrators can call this method"""
        pass

    def get_previous_version(self):
        """ Returns the previous version of this community"""
        pass

    def get_schema_list(self):
        """Returns the SchemaList object, specific for this community"""
        pass

    def is_admin(user_id):
        """ Returns True if the specified user is a community administrator
            of this community"""
        pass

    def get_admins(self):
        """ Returns a list of user ids representing community administrators.
            Adding a new admin possible only from B2ACCESS ??? """
        pass


###############################################################################

class SchemaList:
    """ A SchemaList object represents the list of schemas accepted by a
        community"""

    @staticmethod
    def get_basic_schema():
        """Returns the basic Schema object, common for all communities"""
        pass

    def __getitem__(self, index):
        """Returns the SchemaField with the specified index in the list"""
        pass

    def __iter__(self):
        """Iterates through all the schema objects in the current SchemaList"""
        pass

    def insert(self, index, new_schema):
        """Inserts the new Schema object given as a parameter in the list."""
        pass

    def delete(self, index):
        """Deletes Schema object from the list"""
        pass

class Schema:
    """ A Schema object is essentially an ordered list of SchemaFields.
        The order is relevant for GUIs. A schema field is identified
        by its name. A Schema object cannot be ever deleted"""
    def __getitem__(self, schema_field_name):
        """Returns a SchemaField with the specified name"""
        pass
    def __iter__(self):
        """Iterates through all the schema fields"""
        pass
    def insert(self, index, new_schema_field):
        """Inserts the SchemaField object given as param"""
        pass

class SchemaField:
    """ A dict class describing one metadata field, with a list of
        required keys. Changing a SchemaField is allowed but it must not
        change the semantics of the field. Only minor edits or typo fixes
        should be performed, or enlarging the controlled vocabulary"""
    def __init__(self, schema_field_dict):
        self.dict = schema_field_dict
        for k in ['name', 'col_type', 'display_text', 'description',
            'required', 'cardinality',
            'advanced', # advanced is for the UI (a not-so-important field)
            'data_provide', 'data_source']:
            assert k in schema_field_dict

###############################################################################

class RecordRegistry:
    @staticmethod
    def get_by_id(record_id):
        """ Returns record object, or just a part of the actual record,
            depending on the current_user's access rights."""
        pass

    @staticmethod
    def search_by_filter(filter):
        """ Returns a list of matching record objects, accessible to the
            current user; filter is of type RecordSearchFilter"""
        pass

    @staticmethod
    def create_empty_record():
        """ Returns an empty record object, owned by current user. The default
            state of record_status is 'draft'"""
        pass

    @staticmethod
    def delete_record(record_id):
        """Marks the record as deleted. Only available to superadmins"""
        pass


class RecordSearchFilter:
    def __init__(self, criteria, sort):
        criteria = {                       # implicit AND between criteria
            "__any__": "cern pentaquarks",  # search in any field
            "author":"Smith",              # search for author Smith
            "record_status": "released"    # record must be released
        }
        sort = [                            # must be a list
            ("author", "ascending"),        # because the order is relevant
            ("date", "descending")
        ]


class Record:
    def get_id(self):
        """Returns the record's id"""
        pass

    def get_community_id(self):
        """Returns the record's community id"""
        pass

    def get_previous_version(self):
        """Returns the record's previous version, if any."""
        pass

    def get_metadata_blocks(self):
        """ Returns a MetadataBlockList"""
        pass

    def get_reference_list(self):
        """Returns a ReferenceList object describing the record's references"""
        pass

    def get_file_container(self):
        """Returns the root FileContainer object"""
        pass

    def change_state(self, new_state, reason):
        """ Changes the internal record_status field and triggers other events
            accordingly: if submitted inform the admin for review, if rejected
            inform the owner.
            If new_state == released, automatically creates a new record version."""
        pass


class MetadataBlockList:
    """ MetadataBlockList manages the list of metadata blocks for a particular
        record. """
    def __getitem__(self, index):
        """Returns the MetadataBlock with the specified index"""
        pass
    def __iter__(self):
        """Iterates through all the metadata blocks"""
        pass
    def insert(self, index, new_metadata_block):
        """ Inserts a new metadata block.
            Automatically creates a new record version."""
        pass
    def delete(self, index):
        """ Deletes a metadata_block.
            REQUIREMENT: record_status == 'draft'."""
        pass


class MetadataBlock:
    def get_schema_id(self):
        """ Returns the schema_id of this metadata block"""
        pass

    def get_metadata(self):
        """ Returns a lists of MetadataBlock objects with the all basic and community specific
            metadata fields and values"""
        pass

    def patch_metadata(self, metadata_dict_patch):
        """ Patches the existing metadata with new metadata.
            REQUIREMENT: record_status == 'draft'."""
        pass


class ReferenceList:
    """ ReferenceList manages the list of references for a particular record.
        The references are either ids of records in the same b2share instance
        or PIDs that can point to b2share records in other b2share instances or
        to other resources in general"""
    def __getitem__(self, index):
        """Returns a Reference with the specified index"""
        pass
    def __iter__(self):
        """Iterates through all the references"""
        pass
    def insert(self, index, new_reference):
        """ Inserts a new reference.
            REQUIREMENT: record_status == 'draft'."""
        pass
    def delete(self, index):
        """ Deletes a reference.
            REQUIREMENT: record_status == 'draft'."""
        pass


class Reference:
    """A reference object"""
    def get_relation_type(self):
        """ Returns the relation between the record and the reference. ??? """
        pass
    def get_uri(self):
        """ Returns the reference in a URI form"""
        pass
    def is_local_record(self):
        """ Returns True if the reference is a record in the same b2share
            instance"""
        pass
    def get_as_record(self):
        """ Returns the reference as a Record object, or None if the reference
            does not point to a local record"""
        pass


class FileContainer:
    """A FileContainer can contain other FileContainer objects and also
        File objects. It is like a file system directory. Each FileContainer
        has its own unique ID, but the names must still be unique to simplify
        download and management """

    def get_info(self):
        """Returns a dict with the FileContainer's id, name and URL"""
        pass

    def set_name(self, new_name):
        """ Renames the conatainer. This operation can fail if there exists a folder or file with the same name in the same parent folder.
            REQUIREMENT: record_status == 'draft'."""
        pass

    def add_sub_container(self, new_file_container_name):
        """ Adds a new FileContainer as subcontainer of this one.
            REQUIREMENT: record_status == 'draft'."""
        pass

    def delete_sub_container(self, sub_container_id):
        """ Deletes the subcontainer. Fails if the subcontainer is not empty.
            REQUIREMENT: record_status == 'draft'."""
        pass

    def list_files(self):
        """Returns a list of all the File objects in this FileContainer"""
        pass

    def add_file(self, new_file_name, new_file_URL):
        """ Adds a new File object. The new_file_URL can be a local file path
            or a real http URL. The implementation must create and manage a
            copy of the data (not refer to external resources).
            REQUIREMENT: record_status == 'draft'."""
        pass


class File:
    """A File has a unique ID per Record, and the file's URL is build using
        this ID. Changing the name of a file does not change its URL. The
        directory tree structure of a Record is just metadata."""

    def get_info(self):
        """Returns a dict with this file's id, name, mimetype, size and URL"""
        pass

    def set_name(self, new_name):
        """ Renames the file. This operation can fail if there exists a folder
            or file with the same name in the same parent folder.
            REQUIREMENT: record_status == 'draft'."""
        pass

    def delete(self):
        """Automatically creates a new record version.
            REQUIREMENT: record_status == 'draft'."""
        pass
