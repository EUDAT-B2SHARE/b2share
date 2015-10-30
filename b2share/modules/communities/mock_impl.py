# -*- coding: utf-8 -*-
# B2SHARE

from __future__ import absolute_import
from .api import CommunityRegistryInterface, CommunityInterface

class CommunityRegistry(CommunityRegistryInterface):
    communities = []

    @staticmethod
    def get_by_id(community_id):
        for c in CommunityRegistry.communities:
            if community_id == c["id"]:
                return c
        return None

    @staticmethod
    def get_by_name(community_name):
        for c in CommunityRegistry.communities:
            if community_name == c["name"]:
                return c
        return None

    @staticmethod
    def get_all(start=0, stop=20):
        return CommunityRegistry.communities[start:stop]

    @staticmethod
    def create_community(name, description, logo):
        id = 1 + len(CommunityRegistry.communities)
        c = Community(id, name, description, logo)
        CommunityRegistry.communities.append(c)
        return c

class Community(CommunityInterface):
    def __init__(self, id, name, description, logo):
        self.id = id
        self.name = name
        self.description = description
        self.logo = logo
        self.admin_ids = []
        self.schemas = []
        self.prev_version = None

    def get_description(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "logo": self.logo,
        }

    def patch_description(self, patch_dict):
        self.name = patch_dict['name'] if 'name' in patch_dict else self.name
        self.description = patch_dict['description'] if 'description' in patch_dict else self.description
        self.logo = patch_dict['logo'] if 'logo' in patch_dict else self.logo

    def get_previous_version(self):
        return self.prev_version

    def get_schema_list(self):
        return self.schemas

    def is_admin(self, user_id):
        return user_id in self.admin_ids

    def get_admins(self):
        return self.user_admins


def mock_init():
    CommunityRegistry.create_community(
        "Eudat",
        "The big Eudat community. Use this community if no other is suited for you",
        "eudat.png")
    CommunityRegistry.create_community(
        "Clarin",
        "The Clarin linguistics community",
        "clarin.png")

mock_init()
