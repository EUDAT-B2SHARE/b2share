# -*- coding: utf-8 -*-

from __future__ import absolute_import

from flask.ext.restful import Resource

from .mock_impl import CommunityRegistry, Community

class CommunityListResource(Resource):
    def get(self, **kwargs):
        """
        Retrieve list of communities.
        """
        try:
            ret = []
            for c in CommunityRegistry.get_all():
                ret.append(c.get_description())
            return {'communities': ret}
        except Exception as xc:
            return {'message':'Server Error', 'status':500, 'error': xc}, 500

    def post(self, **kwargs):
        """
        Creates a new community that has associated a new metadata fieldset.
        Only administrators can use it.
        parameter: name, description, logo
        """
        try:
            return CommunityRegistry.create_community(kwargs)
        except Exception as xc:
            return {'message':'Server Error', 'status':500, 'error': xc}, 500


class CommunityResource(Resource):
    def get(self, community_id, **kwargs):
        """
        Get a community metadata and description.
        """
        try:
            return CommunityRegistry.get_by_id(community_id).get_description()
        except Exception as xc:
            return {'message':'Server Error', 'status':500, 'error': xc}, 500

    def patch(self, community_id, **kwargs):
        """
        Modify a community
        """
        try:
            return CommunityRegistry.get_by_id(community_id).patch_description(kwargs)
        except Exception as xc:
            return {'message':'Server Error', 'status':500, 'error': xc}, 500


def setup_app(app, api):
    api.add_resource(CommunityListResource, '/api/communities')
    api.add_resource(CommunityResource, '/api/communities/<int:community_id>')
