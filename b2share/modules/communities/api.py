# -*- coding: utf-8 -*-
# B2SHARE2.api.py

from __future__ import absolute_import

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

