# -*- coding: utf-8 -*-
# B2SHARE2.api.py

from __future__ import absolute_import

# TODO:
#   - schemas change to new schemas with new ids
#   - deprecate a schema in favour of a new one




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

