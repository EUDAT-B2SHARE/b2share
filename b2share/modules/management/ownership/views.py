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
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""B2Share Record-Ownership REST API"""

from __future__ import absolute_import

from functools import wraps

from flask import Blueprint, abort, current_app, request,  jsonify, make_response
from flask_login import current_user
from flask_security.decorators import auth_required

from invenio_rest import ContentNegotiatedMethodView
from invenio_db import db
from invenio_pidstore.models import PersistentIdentifier
from invenio_records.api import Record
from invenio_accounts.models import User
from invenio_pidstore.errors import PIDDoesNotExistError

from b2share.utils import get_base_url
from b2share.modules.management.ownership.cli import find_version_master, pid2record

blueprint = Blueprint('b2share_ownership', __name__)

#@beartype


def add_ownership(pid, user_id: int):
    """
    Set user_id as a new owner for the record (given the record pid)
    :params     pid : record pid
                user_id : id of the user to add as a owner
    """
    record = pid2record(pid)
    if user_id in record['_deposit']['owners']:
        current_app.logger.warning(
            "OWN-API: User is already an owner of the record, skipping..", exc_info=True)
        current_app.logger.warning("OWN-API: Owners are {}".format(" ".join([str(User.query.filter(
            User.id.in_([i])).all()[0]) for i in record['_deposit']['owners']])), exc_info=True)
        abort(400, description="User is already an owner of the record.")
    current_app.logger.info("OWN-API: User {} is an owner. Changing the ownership ...".format(str(User.query.filter(
        User.id.in_([user_id])).all()[0].email)))
    record['_deposit']['owners'].append(user_id)
    current_app.logger.info("OWN-API: Updated users: {}".format("\n".join([str(User.query.filter(
        User.id.in_([i])).all()[0].email) for i in record['_deposit']['owners']])))
    with current_app.test_request_context('/', base_url=get_base_url()):
        record.commit()
        db.session.commit()


def pass_user_email(f):
    """Decorator to retrieve a user."""
    @wraps(f)
    def inner(self, record, user_email, *args, **kwargs):
        user = User.query.filter(User.email == user_email).one_or_none()
        if user is None:
            abort(400, description="User not found in the db.")
        return f(self, record, user, *args, **kwargs)
    return inner


def pass_record(f):
    """Decorator to retrieve a record."""
    @wraps(f)
    def inner(self, record_pid, user_email, *args, **kwargs):
        try:
            record = pid2record(record_pid)
        except PIDDoesNotExistError as e:
            abort(404)
        if record is None:
            abort(404)
        return f(self, record, user_email, *args, **kwargs)
    return inner


def pass_record_ownership(f):
    """Decorator to check if current user is an owner of the record."""
    @wraps(f)
    def inner(self, record, user, *args, **kwargs):
        if not current_user.is_authenticated:
            abort(401)
        if not current_user.id in record['_deposit']['owners']:
            current_app.logger.warning(
                "OWN-API: User is not allowed to change ownership. skipping..", exc_info=True)
            current_app.logger.warning("OWN-API: Owners are: {}".format("\n            ".join([str(User.query.filter(
                User.id.in_([i])).all()[0].email) for i in record['_deposit']['owners']])), exc_info=True)
            abort(403)
        return f(self, record, user, *args, **kwargs)
    return inner


class OwnershipRecord(ContentNegotiatedMethodView):
    """Ownership Management records."""

    view_name = 'record_ownership'

    def __init__(self, *args, **kwargs):
        """Constructor."""
        default_media_type = 'application/json'
        super(OwnershipRecord, self).__init__(
            default_method_media_type={
                'GET': 'application/json',
                #'PUT': 'application/json',
            },
            default_media_type='application/json', *args, **kwargs)

    # @auth_required('token', 'session')
    # @pass_record
    # @pass_user_email
    # @pass_record_ownership
    # def put(self, record, user, **kwargs):
    #     """Set user_id as a new owner of the record
    #     The function will retrive all the version of the
    #     record and will update the ownership for all of them
    #     """
    #     record_pid = record['_deposit']['pid']['value']
    #     user_id = user.id
    #     version_master = find_version_master(record_pid)
    #     all_pids = [v.pid_value for v in version_master.children.all()]
    #     for single_pid in all_pids:
    #         add_ownership(single_pid, user_id)
    #     return make_response(("User {} is now owner of the records {}".format(user.email, " - ".join(all_pids)), 200))

    @auth_required('token', 'session')
    @pass_record
    @pass_user_email
    @pass_record_ownership
    def get(self, record, user, **kwargs):
        """ Test function to check if authn is working. """
        """ Record and User are resolved using the decorators """
        # return make_response(("You can modify the file!<br> PID: {}<br>new owner: {}<br>previous owners: {}".format(
        #     str(record['_deposit']['pid']['value']),
        #     str(user.email),
        #     ", ".join([str(User.query.filter(
        #         User.id.in_([i])).all()[0].email) for i in record['_deposit']['owners']])

        # ), 200))
        abort(501, description="Ownership API not available at the moment")
        #return make_response(("API not available at the moment"), 501)


blueprint.add_url_rule(
    '/records/<string:record_pid>/ownership/<string:user_email>',
    view_func=OwnershipRecord.as_view(
        OwnershipRecord.view_name
    )
)
