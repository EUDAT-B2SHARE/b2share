# -*- coding: utf-8 -*-
# B2SHARE2

from __future__ import absolute_import
import abc

# TODO:
#   - schemas change to new schemas with new ids
#   - deprecate a schema in favour of a new one

# a schema belongs to a community, but can be also used by another community


class SchemaRegistryInterface(object):
    """ A SchemaList object represents the list of schemas accepted by a
        community"""

    @staticmethod
    @abc.abstractmethod
    def get_basic_schema():
        """Returns the basic Schema object, common for all communities"""
        pass

    @staticmethod
    @abc.abstractmethod
    def get_by_id(schema_id):
        """Returns a Schema object, based on its id"""
        pass

    @staticmethod
    @abc.abstractmethod
    def get_by_community_id(community_id):
        """Returns a Schema object, based on its community id"""
        pass

    @staticmethod
    @abc.abstractmethod
    def get_all(start=0, stop=20):
        """Returns all schema objects"""
        pass


class SchemaInterface(object):
    """ A Schema object is a shallow object encapsulating a jsonschema object.
        A Schema cannot be ever deleted"""

    @abc.abstractmethod
    def get_id(self):
        """Returns the id of the schema"""
        pass

    @abc.abstractmethod
    def get_community_id(self):
        """Returns the id of the owning community"""
        pass
