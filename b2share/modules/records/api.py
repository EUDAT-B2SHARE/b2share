# -*- coding: utf-8 -*-
#
# This file is part of EUDAT B2Share.
# Copyright (C) 2016 University of Tuebingen, CERN.
# Copyright (C) 2015 University of Tuebingen.
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

from __future__ import absolute_import, print_function

import uuid

from invenio_db import db
from invenio_pidstore.minters import recid_minter
from invenio_records.api import Record as InvenioRecord
from invenio_records.models import RecordMetadata
from invenio_search import Query, current_search_client


# TODO:
#   - versioning of records:
#   - flat list of files? with pagination?


class RecordSearchFilter(object):
    def __init__(self, query, sort=None, start=0, stop=10):
        """criteria = {                       # implicit AND between criteria
            "__any__": "cern pentaquarks",  # search in any field
            "author":"Smith",              # search for author Smith
            "record_status": "released"    # record must be released
        }
        sort = [                            # must be a list
            ("author", "ascending"),        # because the order is relevant
            ("date", "descending")
        ]"""
        self.query = query
        self.sort = sort or []
        self.start = int(start)
        self.stop = int(stop)


class Record(object):
    @classmethod
    def get_by_id(cls, record_id):
        """ Returns record object, or just a part of the actual record,
            depending on the current_user's access rights."""
        record_id = str(record_id)
        r = db.session.query(RecordMetadata).filter(RecordMetadata.id == record_id).one_or_none()
        return Record(r) if r else None

    @classmethod
    def search_by_filter(cls, search_filter):
        """ Returns a list of matching record objects, accessible to the
            current user; filter is of type RecordSearchFilter"""

        query = Query(search_filter.query)[search_filter.start:search_filter.stop]
        for sort_key in search_filter.sort:
            if sort_key:
                query = query.sort(sort_key)

        response = current_search_client.search(
            index='records',
            doc_type='record',
            body=query.body,
            version=True,
        )
        hits = response.get('hits').get('hits')
        return hits

    @classmethod
    def list(cls, start=0, stop=10):
        """ Returns a list of records"""
        start = int(start)
        stop = int(stop)
        all_records = db.session.query(RecordMetadata).limit(stop)[start:]
        return [Record(r) for r in all_records]

    @classmethod
    def create(cls, data):
        """ Returns a record object, owned by current user. The default
            state of record_status is 'draft'"""
        data = data or {}

        record_uuid = uuid.uuid4()
        recid_minter(record_uuid, data)
        record = InvenioRecord.create(data, id_=record_uuid)
        db.session.commit()

        current_search_client.index(
            index='records',
            doc_type='record',
            id=record.id,
            body=data,
            version=1,
            version_type='external_gte',
        )

        return Record(record.model)

    @classmethod
    def delete_record(cls, record_id):
        """Marks the record as deleted. Only available to superadmins"""
        pass

    def __init__(self, record):
        self.record = record

    def get_id(self):
        """Returns the record's id"""
        return self.record.id

    def get_community_id(self):
        """Returns the record's community id"""
        return self.record.json.get('community_id')

    def get_previous_version(self):
        """Returns the record's previous version, if any."""
        pass

    def get_metadata_blocks(self):
        """ Returns a MetadataBlockList"""
        return MetadataBlockList(self.record)

    def get_reference_list(self):
        """Returns a ReferenceList object describing the record's references"""
        return ReferenceList(self.record)

    def get_file_container(self):
        """Returns the root FileContainer object"""
        return FileContainer(self.record)

    def change_state(self, new_state, reason):
        """ Changes the internal record_status field and triggers other events
            accordingly: if submitted inform the admin for review, if rejected
            inform the owner.
            If new_state == released, automatically creates a new record version."""
        pass


class MetadataBlockList(object):
    """ MetadataBlockList manages the list of metadata blocks for a particular
        record. """
    def __init__(self, record):
        self.record = record

    def __getitem__(self, index):
        """Returns the MetadataBlock with the specified index"""
        md = self.record.json.get('metadata')
        return md[index]

    def __iter__(self):
        """Iterates through all the metadata blocks"""
        md = self.record.json.get('metadata')
        for md_block in md:
            yield md_block

    def patch_block(self, metadata_dict_patch):
        """ Patches the existing metadata with new metadata.
            REQUIREMENT: record_status == 'draft'."""
        pass

    def insert(self, index, new_metadata_block):
        """ Inserts a new metadata block.
            Automatically creates a new record version."""
        pass

    def delete(self, index):
        """ Deletes a metadata_block.
            REQUIREMENT: record_status == 'draft'."""
        pass


class ReferenceList(object):
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


class Reference(object):
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


class FileContainer(object):
    """A FileContainer can contain other FileContainer objects and also
        File objects. It is like a file system directory. Each FileContainer
        has its own unique ID, but the names must still be unique to simplify
        download and management """

    def get_info(self):
        """Returns a dict with the FileContainer's id, name and URL"""
        pass

    def set_name(self, new_name):
        """ Renames the conatainer. This operation can fail if there exists a
            folder or file with the same name in the same parent folder.
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

    def get_file(self, file_id):
        """Returns a File object in this FileContainer"""
        pass

    def add_file(self, new_file_name, new_file_URL):
        """ Adds a new File object. The new_file_URL can be a local file path
            or a real http URL. The implementation must create and manage a
            copy of the data (not refer to external resources).
            REQUIREMENT: record_status == 'draft'."""
        pass


class File(object):
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


