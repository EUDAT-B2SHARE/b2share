# -*- coding: utf-8 -*-
#
# This file is part of EUDAT B2Share.
# Copyright (C) 2017 University of Tübingen, CERN
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

"""B2Share cli commands for Record-Ownership."""


from __future__ import absolute_import, print_function

import click

from flask.cli import with_appcontext
from flask import current_app

from invenio_db import db
from invenio_pidstore.models import PersistentIdentifier, PIDStatus
from invenio_records_files.api import Record
from invenio_accounts.models import User
from invenio_pidrelations.contrib.versioning import PIDVersioning
from invenio_pidstore.errors import PIDDoesNotExistError

from b2share.utils import get_base_url


def render_error(error, pid, action):
    raise click.ClickException(click.style(error, fg="red") + "\t\tb2recPID: " +
                     click.style(pid, fg="blue") + "\t\tAction: {}".format(action))
    # click.ClickException("Error: {}\t\tb2recPID: {}\t\tAction: {}".format(error, pid,action))


def pid2record(pid):
    pid = PersistentIdentifier.get('b2rec', pid)
    return Record.get_record(pid.object_uuid)


def replace_ownership(pid, user_id: int):
	record = pid2record(pid)
	record['_deposit']['owners'] = [user_id]
	with current_app.test_request_context('/', base_url=get_base_url):
		record.commit()
		db.session.commit()


def add_ownership(pid, user_id: int):
    record = pid2record(pid)
    if user_id not in record['_deposit']['owners']:
        record['_deposit']['owners'].append(user_id)
        with current_app.test_request_context('/', base_url=get_base_url):
            record.commit()
            db.session.commit()
    else:
        render_error("User is already owner of record",
                     pid, "skipping")


def remove_ownership(pid, user_id: int):
    record = pid2record(pid)
    if user_id in record['_deposit']['owners']:
        if len(record['_deposit']['owners']) > 1:
            try:
                record['_deposit']['owners'].remove(user_id)
                with current_app.test_request_context('/', base_url=get_base_url):
                    record.commit()
                    db.session.commit()
            except ValueError as e:
                click.secho("%s\t%s" % (pid, str(User.query.filter(
                    User.id.in_([user_id])).all()[0].email)))
                raise ValueError() from e
        else:
            render_error("Record has to have at least one user",
                         pid, "skipping remove")
    else:
        render_error("User is not an owner of record",
                     pid, "skipping")


def list_ownership(record_pid):
    version_master = find_version_master(record_pid)
    all_pids = [v.pid_value for v in version_master.children.all()]
    click.secho("PID\t\t\t\t\tOwners", fg='green')
    for single_pid in all_pids:
        record = pid2record(single_pid)
        owners = record['_deposit']['owners']
        click.secho("%s\t%s" % (
            single_pid,
            " ".join([str(User.query.filter(
                User.id.in_([w])).all()[0].email) for w in owners])))


def check_user(user_email):
    return User.query.filter(User.email == user_email).one_or_none()


@click.group()
def ownership():
    """ownership management commands."""


def find_version_master(pid):
    """Retrieve the PIDVersioning of a record PID.

    :params pid: record PID.
    """
    from b2share.modules.deposit.errors import RecordNotFoundVersioningError
    from b2share.modules.records.providers import RecordUUIDProvider
    try:
        child_pid = RecordUUIDProvider.get(pid).pid
        if child_pid.status == PIDStatus.DELETED:
            raise RecordNotFoundVersioningError()
    except PIDDoesNotExistError as e:
        raise RecordNotFoundVersioningError() from e

    return PIDVersioning(child=child_pid)


@ownership.command()
@with_appcontext
@click.argument('record-pid', required=True, type=str)
def list(record_pid):
    """ Checks that ownership of all the record versions of given a single record id.

    :params record-pid: B2rec record PID
    """
    list_ownership(record_pid)


@ownership.command()
@with_appcontext
@click.argument('record-pid', required=True, type=str)
@click.argument('user-email', required=True, type=str)
@click.option('-q', '--quiet', is_flag=True, default=False)
@click.option('-y', '--yes-i-know', is_flag=True, default=False)
def reset(record_pid, user_email, yes_i_know, quiet):
    """ Remove the previous ownership and set up the new user as a unique owner for all the version of the record.

    :params record-pid: B2rec record PID
            user-email: user email
    """
    if check_user(user_email) is None:
        raise click.ClickException(
            click.style(
                """User does not exist. Please check the email and try again""", fg="red"))
    list_ownership(record_pid)
    if yes_i_know or click.confirm(
            "Are you sure you want to reset the owership? Previous owners will not be able to access the records anymore.", abort=True):
        version_master = find_version_master(record_pid)
        all_pids = [v.pid_value for v in version_master.children.all()]
        user = User.query.filter(User.email == user_email).one_or_none()
        for single_pid in all_pids:
            replace_ownership(single_pid, user.id)
    if not quiet:
        click.secho("Ownership Updated!", fg='red')
        list_ownership(record_pid)


@ownership.command()
@with_appcontext
@click.argument('record-pid', required=True, type=str)
@click.argument('user-email', required=True, type=str)
@click.option('-q', '--quiet', is_flag=True, default=False)
def add(record_pid, user_email, quiet):
    """ Add user as owner for all the version of the record.
    
    :params record-pid: B2rec record PID
        user-email: user email
    """
    if check_user(user_email) is None:
        raise click.ClickException(
            """User does not exist. Please check the email and try again""")
    version_master = find_version_master(record_pid)
    all_pids = [v.pid_value for v in version_master.children.all()]
    user = User.query.filter(User.email == user_email).one_or_none()
    for single_pid in all_pids:
        add_ownership(single_pid, user.id)
    if not quiet:
        click.secho("Ownership Updated!", fg='red')
        list_ownership(record_pid)


@ownership.command()
@with_appcontext
@click.argument('record-pid', required=True, type=str)
@click.argument('user-email', required=True, type=str)
@click.option('-q', '--quiet', is_flag=True, default=False)
def remove(record_pid, user_email, quiet):
    """ Remove user as an owner of the record.
    
    :params record-pid: B2rec record PID
        user-email: user email
    """
    if check_user(user_email) is None:
        raise click.ClickException(
            """User does not exist. Please check the email and try again""")

    version_master = find_version_master(record_pid)
    all_pids = [v.pid_value for v in version_master.children.all()]
    user = User.query.filter(User.email == user_email).one_or_none()
    for single_pid in all_pids:
        remove_ownership(single_pid, user.id)
    if not quiet:
        click.secho("Ownership Updated!", fg='red')
        list_ownership(record_pid)
