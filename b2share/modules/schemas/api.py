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
