# -*- coding: utf-8 -*-
# B2SHARE2


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
