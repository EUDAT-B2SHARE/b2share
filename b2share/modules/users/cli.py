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

"""B2Share cli commands for records.

Account_User table is linked to multiple tables in the db.
You can see the dependency graph from the DOT notation:

access_actionsroles -> accounts_role  [label="role_id-id"];
accounts_userrole -> accounts_role  [label="role_id-id"];
access_actionsusers -> accounts_user  [label="user_id-id"];
accounts_user_session_activity -> accounts_user  [label="user_id-id"];
accounts_userrole -> accounts_user  [label="user_id-id"];
oauth2server_client -> accounts_user  [label="user_id-id"];
oauth2server_token -> accounts_user  [label="user_id-id"];
oauthclient_remoteaccount -> accounts_user  [label="user_id-id"];
oauthclient_useridentity -> accounts_user  [label="id_user-id"];
transaction -> accounts_user  [label="user_id-id"];
files_bucket -> files_location  [label="default_location-id"];
oauthclient_remotetoken -> oauthclient_remoteaccount  [label="id_remote_account-id"];

To delete the account we need:

1- Delete the Remote Accounts linked to the Account:
    To do this, we need to delete the remoteToken linked to the Remote Account
    This action could not be straightforward if we have changed the SECRET_KEY in
    config. The key is use to decript the token. If it has changed, it will 
    raise a UnicodeDecodeError.
    To solved the problem, we could reset temporary the old SECRET KEY to remove
    the RemoteToken.

    from invenio import current_app
    from invenio_db import db
    print(current_app.config.get('SECRET_KEY'))
    current_app.secret_key = <new_secret_key>
    db.session.expunge_all()
    print(current_app.config.get('SECRET_KEY'))

2- Remove the UserIdentity object:

    from invenio_db import db
    from invenio_oauthclient.models import UserIdentity
    with db.session.begin_nested():
        UserIdentity.query.filter_by(id_user=user.id).delete()

3- Delete records from transaction table. In the transaction table information
    every time we are committing to the db, a log will be stored with user id,
    timestamp and IP adress of the location. This will not be deleted with 
    cascade delete. 

    from invenio_db import db
    from flask import current_app
    with current_app.app_context():
        db.engine.execute('DELETE FROM transaction WHERE user_id={};'.format(user.id))

"""


from __future__ import absolute_import, print_function

import click
import requests
from tabulate import tabulate

from flask.cli import with_appcontext
from flask import current_app

from werkzeug.local import LocalProxy

from invenio_db import db
from invenio_accounts.cli import users
from invenio_accounts.models import User
from invenio_oauthclient.models import UserIdentity, RemoteAccount
from flask_security.utils import hash_password


@users.command('list')
@with_appcontext
def users_list():
    """List all known users"""

    userdata = User.query.order_by(User.id)

    headers = ['ID', 'ACTIVE', 'EMAIL', 'ROLES']
    click.secho((tabulate([[u.id,
            u.active,
            u.email,
            u.roles if len(u.roles) else 'None'] for u in userdata], headers=headers)))

@users.command('find')
@with_appcontext
@click.option('-u','--user_id', is_flag=False, default=None, type=int)
@click.option('-e','--user_email', is_flag=False, default=None, type=str)
def user_info(user_id, user_email):
    """Get user info user user_id or user_email.
    If you use both of them only the user_id will be used.
    """

    user_data = get_user(user_id, user_email)
    if user_data is None:
        raise click.ClickException("No user found with user_id=<{}> and user_email=<{}>")    

    headers = ['ID', 'ACTIVE', 'EMAIL', 'ROLES']
    click.secho((tabulate([[user_data.id,
            user_data.active,
            user_data.email,
             user_data.roles if len(user_data.roles) else 'None']], headers=headers)))


@users.command('delete')
@with_appcontext
@click.option('-u','--user_id', is_flag=False,  type=int)
@click.option('-e','--user_email', is_flag=False, default=None, type=str)
def del_user(user_id, user_email):
    """delete a user given a user_id or a user_email.
    If you use both of them only the user_id will be used.
    """
    user = get_user(user_id, user_email)
    if not user_data:   
            click.secho("No user found with user_id=<{}> and user_email=<{}>".format(user_id,user_email))    
    else:
        if not check_ownership(user):
            user_data = delete_user(user)
            click.secho("User successfully deleted")
        else:
            raise click.ClickException("It is not possible to delete the user because the user is an active owner of records/drafts")
      
@users.command('anonymize')
@with_appcontext
@click.option('-u','--user_id', is_flag=False,  type=int)
@click.option('-e','--user_email', is_flag=False, default=None, type=str)
def anonymize_user(user_id, user_email):
    """delete a user given a user_id or a user_email.
    If you use both of them only the user_id will be used.
    """
    user = get_user(user_id, user_email)
    if not user_data:
            click.secho("No user found with user_id=<{}> and user_email=<{}>".format(user_id,user_email))    
    else:
        if not check_ownership(user):
            user_data = anonymize_user(user)
            click.secho("User successfully anonymized")
        else:
            raise click.ClickException("It is not possible to update the user because the user is an active owner of records/drafts")


def get_user(user_id=None, user_email=None):
    if user_id is not None:
        return User.query.filter(User.id == int(user_id)).one_or_none()
    elif user_email is not None:
        return User.query.filter(User.email == user_email).one_or_none()
    else:
        return None


def check_ownership(user):
    from b2share.utils import ESSearch
    query = 'owners:{} || _deposit.owners:{} '.format(user.id, user.id)
    es = ESSearch()
    es.search(query=query)
    return es.matches()

def delete_user(user):
    if user is None:
        raise click.ClickException("No user found with user_id=<{}> and user_email=<{}>")    
    click.secho("found user: {}".format(str(user)))

    with db.session.begin_nested():
        UserIdentity.query.filter_by(id_user=user.id).delete()
        click.secho("deleting UserIdentity object ...")
    with db.session.begin_nested():
        user=get_user(user_id=user.id,user_email=user.email)
        
        for remote_account in user.remote_accounts:
            try:
                remote_account.delete()
            except UnicodeDecodeError as e:
                # remote_token was created with a SECRET_KEY different from the current one
                # when we are intializating the RemoteToken, the token cannot be decoded
                # To solve this problem we can manually delete the entry in the db  
                click.secho("Cascade delete failed for remote_tokens.\nForce-removing the token...")
                with current_app.app_context():
                    db.engine.execute('DELETE FROM oauthclient_remotetoken WHERE id_remote_account={};'.format(remote_account.id))
                click.secho("Remote Token removed from the db.")

    # remove user from the transaction table

    with current_app.app_context():
        #db.engine.execute('DELETE FROM transaction WHERE user_id={};'.format(user.id))
        db.engine.execute('UPDATE transaction SET user_id = NULL WHERE user_id={};'.format(remote_account.id))
        db.session.commit()

    db.session.delete(user)
    db.session.commit()
    click.secho("deleting User object ...")

    assert get_user(user.id, user.email) == None
    assert UserIdentity.query.filter_by(id_user=user.id).one_or_none() == None

    return True



def user_update(user):
    user.email="anonymous_user_{}".format(user.id)
    user.password=hash_password("deleted_user_{}".format(user.id))
    return user


def anonymize_user(user):
    if user is None:
         raise click.ClickException("No user found with user_id=<{}> and user_email=<{}>")    
    click.secho("found user: {}".format(str(user)))

    with db.session.begin_nested():
        UserIdentity.query.filter_by(id_user=user.id).delete()
        click.secho("deleting UserIdentity object ...")
    with db.session.begin_nested():
        user=get_user(user_id=user.id,user_email=user.email)
        
        for remote_account in user.remote_accounts:
            try:
                remote_account.delete()
            except UnicodeDecodeError as e:
                # remote_token was created with a SECRET_KEY different from the current one
                # when we are intializating the RemoteToken, the token cannot be decoded
                # To solve this problem we can manually delete the entry in the db  
                click.secho("Cascade delete failed for remote_tokens.\nForce-removing the token...")
                with current_app.app_context():
                    db.engine.execute('SELECT * FROM oauthclient_remotetoken WHERE id_remote_account={};'.format(remote_account.id))
                click.secho("Remote Token removed from the db.")

    previous_user_id,previous_user_email=user.id,user.email
    # here change user
    user=user_update(user)
    db.session.add(user)
    db.session.commit()
    click.secho("anonymizing User object ...")
    return True


