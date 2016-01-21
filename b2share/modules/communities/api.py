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


class CommunityRegistryInterface(object):
    @staticmethod
    @abc.abstractmethod
    def get_by_id(community_id):
        """Returns a Community object or nil"""
        pass

    @staticmethod
    @abc.abstractmethod
    def get_by_name(community_name):
        """Returns a Community object or nil"""
        pass

    @staticmethod
    @abc.abstractmethod
    def get_all(start, stop):
        """Returns all Community objects with index between start and stop"""
        pass

    @staticmethod
    @abc.abstractmethod
    def create_community(json):
        """ The json parameter is a dictionary containing the name, domain,
            description (all strings) and logo (image uri) of the community.
            Returns a newly created community object or raises exception.
            Only administrators can call this function. A new community
            is implicitly associated with a new, empty, schema list. """
        pass


class CommunityInterface(object):
    @abc.abstractmethod
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

    @abc.abstractmethod
    def patch_description(self, patch_dict):
        """ Changes the community description with dict. The community id cannot be changed.
            Only community administrators can call this method"""
        pass

    @abc.abstractmethod
    def get_previous_version(self):
        """ Returns the previous version of this community"""
        pass

    @abc.abstractmethod
    def get_schema_id_list(self):
        """Returns a list of ids of schema objects, specific for this community"""
        pass

    @abc.abstractmethod
    def get_admins(self):
        """ Returns a list of user ids representing community administrators.
            Adding a new admin possible only from B2ACCESS ??? """
        pass
