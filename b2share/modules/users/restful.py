# -*- coding: utf-8 -*-

from __future__ import absolute_import

from flask.ext.restful import Resource

class UserList(Resource):
    def get(self, **kwargs):
        """
        Search for users.
        """
        return None


class User(Resource):
    def get(self, user_id, **kwargs):
        """
        Get a user profile information
        """
        return None


def setup_app(app, api):
    api.add_resource(UserList, '/api/users')
    api.add_resource(User, '/api/users/<int:user_id>')
