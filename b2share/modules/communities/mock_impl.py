# -*- coding: utf-8 -*-
# B2SHARE


from __future__ import absolute_import
from .api import CommunityRegistryInterface, CommunityInterface


class CommunityRegistry(CommunityRegistryInterface):
    communities = []

    @staticmethod
    def get_by_id(community_id):
        community_id = str(community_id)
        for c in CommunityRegistry.communities:
            if community_id == c['id']:
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
    def create_community(json):
        cid = len(CommunityRegistry.communities)
        c = Community(cid, json)
        CommunityRegistry.communities.append(c)
        return c


class Community(CommunityInterface, dict):
    @staticmethod
    def clean(json):
        return {k: json[k] for k in ['name', 'domain', 'description', 'logo']}

    def __init__(self, cid, json):
        dict.__init__(self)
        self.update(self.clean(json))
        self['id'] = str(cid)
        self['previous_version'] = None
        self['schema_id_list'] = []

    def get_description(self):
        return self.clean(self)

    def patch_description(self, patch_dict):
        self.update(self.clean(patch_dict))
        return self

    def get_previous_version(self):
        return self['prev_version']

    def get_schema_id_list(self):
        return self['schema_id_list']

    def add_schema(self, schema_json):
        from ..schemas.mock_impl import SchemaRegistry
        schema_json['community_id'] = self['id']
        schema = SchemaRegistry._add(schema_json)
        self['schema_id_list'].append(schema.get_id())

    def get_admins(self):
        return []


def mock_init():
    from ..schemas.default_schemas import schema_bbmri, schema_clarin

    CommunityRegistry.create_community({
        'name': "EUDAT",
        'domain': "",
        'description': "The big Eudat community. Use this community if no other is suited for you.",
        'logo': "/img/communities/eudat.png"
    })

    CommunityRegistry.create_community({
        'name': "BBMRI",
        'domain': "Biomedical Research",
        'description': 'Biomedical Research data.',
        'logo': "/img/communities/bbmri.png"
    }).add_schema(schema_bbmri)

    CommunityRegistry.create_community({
        'name': "CLARIN",
        'domain': "Linguistics",
        'description': "The Clarin linguistics community.",
        'logo': "/img/communities/clarin.png"
    }).add_schema(schema_clarin)

    CommunityRegistry.create_community({
        'name': "DRIHM",
        'domain': "Hydro-Meteorology",
        'description': 'Meteorology and climate data.',
        'logo': '/img/communities/drihm.png'
    })

    CommunityRegistry.create_community({
        'name': "NRM",
        'domain': "Herbarium",
        'description': "Herbarium data.",
        'logo': "/img/communities/nrm.png"
    })

    CommunityRegistry.create_community({
        'name': "RDA",
        'domain': "Generic",
        'description': "Research Data Alliance data.",
        'logo': "/img/communities/rda.png"
    })


mock_init()
