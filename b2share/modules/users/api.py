# -*- coding: utf-8 -*-
# B2SHARE2

from __future__ import absolute_import

# The current user is implicitly used throughout the API
# from flask.login import current_user

# TODO:
#   - ACL and POLICY definitions


class UserRegistry:
    @staticmethod
    def create_user(nickname, email, full_name, other_info):
        """ Returns a newly created user object, or raises exception."""
        pass

    @staticmethod
    def get_by_id(user_id):
        """Returns a User object or nil"""
        pass

    @staticmethod
    def get_by_name(nickname):
        """ Returns a User object or nil. A nickname uniquely identifies
            one user"""
        pass

    @staticmethod
    def search(part_of_nickname_or_full_name):
        """ Returns a short list of user objects (potential matches)."""
        pass


#from invenio.modules.accounts.models import User as InvenioUser

class User:
    def login(self):
        """ Logs in this user (self), making it the flask current_user
            Raises exception on failure"""
        pass

    def get_info(self, show_private_info=False):
        """ Returns a dict with the user's public info (id, nickname)"""
        pass

    def get_private_info(self, show_private_info=False):
        """ Returns a dict with the user's private info (email, ???)
            or raises AccessDenied exception"""
        pass
