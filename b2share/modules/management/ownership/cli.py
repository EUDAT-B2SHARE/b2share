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
import os
import uuid

from flask.cli import with_appcontext
from flask import app, current_app

from invenio_db import db
from invenio_pidstore.models import PersistentIdentifier, PIDStatus
from b2share.modules.records.api import B2ShareRecord

from invenio_accounts.models import User
from invenio_pidrelations.contrib.versioning import PIDVersioning
from invenio_pidstore.errors import PIDDoesNotExistError

from b2share.modules.deposit.api import Deposit
from b2share.utils import ESSearch, to_tabulate
from b2share.modules.users.cli import get_user

from .errors import UserAlreadyOwner
from .utils import get_record_by_pid, add_ownership_to_record, find_version_master, check_user


def render_error(error, type, pid, action):
    raise click.ClickException(click.style(error, fg="red") + "\t\t{}: ".format(type) +
                               click.style(pid, fg="blue") + "\t\tAction: {}".format(action))


def replace_ownership(pid, user_id: int, obj_type='record'):
    record = get_record_by_pid(pid)
    record['_deposit']['owners'] = [user_id]
    try:
        record = record.commit()
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        click.secho(
            "Error for object {}, skipping".format(pid), fg='red')
        click.secho(e)


def add_ownership(obj, user_id: int, obj_type='record'):
    try:
        add_ownership_to_record(obj, user_id)
    except UserAlreadyOwner as e:
        render_error("User is already owner of object", 'object id',
                     obj['_deposit']['id'], "skipping")
    except Exception as e:
        click.secho(
            "Error for object {}, skipping".format(obj.id), fg='red')
        click.secho(e)


def remove_ownership(obj, user_id: int, obj_type='record'):
    if user_id in obj['_deposit']['owners']:
        if len(obj['_deposit']['owners']) > 1:
            try:
                obj['_deposit']['owners'].remove(user_id)
                obj = obj.commit()
                db.session.commit()
            except ValueError as e:
                db.session.rollback()
                click.secho("%s\t%s" % (obj['_deposit']['id'], str(User.query.filter(
                    User.id.in_([user_id])).all()[0].email)))
                raise ValueError() from e
        else:
            render_error("Record has to have at least one user", 'object id',
                         obj['_deposit']['id'], "skipping remove")
    else:
        render_error("User is not an owner of record", 'object id',
                     obj['_deposit']['id'], "skipping")


def list_ownership(record_pid):
    version_master = find_version_master(record_pid)
    all_pids = [v.pid_value for v in version_master.children.all()]
    click.secho("PID\t\t\t\t\tOwners", fg='green')
    for single_pid in all_pids:
        record = get_record_by_pid(single_pid)
        owners = record['_deposit']['owners']
        click.secho("%s\t%s" % (
            single_pid,
            " ".join([str(User.query.filter(
                User.id.in_([w])).all()[0].email) for w in owners])))


# decorator to patch the current_app.config file temporarely
def patch_current_app_config(vars):
    def decorator(function):
        def inner(*args, **kwargs):
            old_vars = {v: current_app.config.get(
                v, None) for v in vars.keys()}
            for v, val in vars.items():
                if val is None:
                    raise Exception(
                        "Value for var {} is None.\nSet up the variable to run the command.".format(str(v)))
                current_app.config[v] = val
            out = function(*args, **kwargs)
            for v, val in old_vars.items():
                current_app.config[v] = val
            return out
        return inner
    return decorator


@click.group()
def ownership():
    """ownership management commands."""


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
        record = get_record_by_pid(single_pid)
        add_ownership(record, user.id)
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
        record = get_record_by_pid(single_pid)
        remove_ownership(record, user.id)
    if not quiet:
        click.secho("Ownership Updated!", fg='red')
        list_ownership(record_pid)


@ownership.command()
@with_appcontext
@click.argument('user-email', required=True, type=str)
@click.option('-t', '--type', type=click.Choice(['deposit', 'record']), required=False)
def find(user_email, type=None):
    """ Find all the records or/and deposits where user is one of the owners.

    :params user-email: user email
            type: record type (deposit, record)
    """
    if check_user(user_email) is None:
        raise click.ClickException(
            "User <{}> does not exist. Please check the email and try again".format(user_email))
    # user that we want to find in the db
    user = get_user(user_email=user_email)
    if user is not None:
        # search using ESSearch class and filtering by type
        search = search_es(user, type=type)
        if search is not None:
            click.secho(click.style("Current state:", fg="blue"))
            click.secho(to_tabulate(search))
        else:
            click.secho(click.style(
                "No objs found with owner {}".format(str(user)), fg="red"))


def _is_valid_uuid(input_string: str) -> bool:
    """
    Checks if a string is a valid UUID
    """
    try:
        _ = uuid.UUID(input_string)
        return True
    except ValueError:
        return False


def _get_user_by_email_or_id(user_email_or_id: str):
    """
    returns a user by email or id
    """
    # user that we want to replace
    if not _is_valid_uuid(user_email_or_id):
        user_email = user_email_or_id
        if check_user(user_email) is None:
            raise click.ClickException(
                "User <{}> does not exist. Please check the email and try again".format(user_email))
        user = get_user(user_email=user_email)
    else:
        user_id = user_email_or_id
        user = get_user(user_id=user_id)
        if user is None:
            raise click.ClickException(
                "User <{}> does not exist. Please check the id and try again".format(user_id))
    return user


@ownership.command('transfer-add')
@with_appcontext
@click.option('-t', '--type', type=click.Choice(['deposit', 'record']), required=False)
@click.argument('user-email-or-id', required=True, type=str)
@click.argument('new-user-email-or-id', required=True, type=str)
@patch_current_app_config({'SERVER_NAME': os.environ.get('JSONSCHEMAS_HOST')})
def transfer_add(user_email_or_id, new_user_email_or_id):
    """ Add user to all the records or/and deposits if user is not of the owners already.

    :params user-email-or-id: user email or id of the old owner
            new-user-email-or-id: user email or id of the new owner
    """
    user = _get_user_by_email_or_id(user_email_or_id)
    new_user = _get_user_by_email_or_id(new_user_email_or_id)

    changed = False
    if user is not None and new_user is not None:
        # search using ESSearch class and filtering by type
        search = search_es(user, type=type)
        if search is not None:
            # print initial state
            click.secho(click.style("Initial state:", fg="blue"))
            print(to_tabulate(search))

            # update values for each record/deposit
            for id in search.keys():
                obj = Deposit.get_record(id)
                # try to update
                try:
                    with current_app.test_request_context():
                        add_ownership(obj=obj, user_id=new_user.id,
                                      obj_type=search[id]['type'])
                        changed = True
                except click.ClickException as e:
                    click.echo(e)
    if changed:
        final_search = search_es(user, type=type)
        if final_search is not None:
            # print the updated state
            click.secho(click.style("\nFinal state:", fg="blue"))
            print(to_tabulate(final_search))
        click.secho(click.style("Ownership Updated!", fg="green"))
    else:
        click.secho(click.style(
            "It was not possible to update the ownership", fg="red"))

@ownership.command('remove-all')
@with_appcontext
@click.argument('user-email', required=True, type=str)
@click.option('-t', '--type', type=click.Choice(['deposit', 'record']), required=False)
@patch_current_app_config({'SERVER_NAME': os.environ.get('JSONSCHEMAS_HOST')})
def transfer_remove(user_email, type=None):
    """ remove user to all the records or/and deposits.

    :params user-email: user email
            type: record type (deposit, record)
    """
    if check_user(user_email) is None:
        raise click.ClickException(
            "User <{}> does not exist. Please check the email and try again".format(user_email))
   # user that we want to remove
    user = get_user(user_email=user_email)
    changed = False
    if user is not None:
        # search using ESSearch class and filtering by type
        search = search_es(user, type=type)
        if search is not None:
            # print initial state
            click.secho(click.style("Initial state:", fg="blue"))
            print(to_tabulate(search))

            # update values for each record/deposit
            for id in search.keys():
                obj = Deposit.get_record(id)
                # try to delete user
                try:
                    with current_app.test_request_context():
                        remove_ownership(obj=obj, user_id=user.id,
                                         obj_type=search[id]['type'])
                        changed = True
                except click.ClickException as e:
                    click.echo(e)
    if changed:
        final_search = search_es(user, type=type)
        if final_search is not None:
            # print the updated state
            # this should never be printed if the remove has succeeded
            click.secho(click.style("\nFinal state:", fg="blue"))
            print(to_tabulate(final_search))
        click.secho(click.style("Ownership Updated!", fg="green"))
    else:
        click.secho(click.style(
            "It was not possible to update the ownership", fg="red"))


def search_es(user, type):
    '''
    use ESSearch to find obj where user is owner

    :params  user: User obj
             type: filter the query. Possible values (deposit, record or None)
    '''

    query = 'owners:{} || _deposit.owners:{}'.format(user.id, user.id)
    if type == 'deposit':
        query = '_deposit.owners:{}'.format(user.id)
    elif type == 'record':
        query = 'owners:{}'.format(user.id)

    es = ESSearch()
    es.search(query=query)
    if es.matches():
        search_result = es.get_ownership_info()
        return search_result
    else:
        click.secho("The search has returned 0 maches.")
        return None
