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
