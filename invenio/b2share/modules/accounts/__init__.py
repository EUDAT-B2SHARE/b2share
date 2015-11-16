"""
B2SHARE
"""

from flask import flash, url_for

from invenio.base.globals import cfg

from invenio.base.i18n import _

from flask.ext.login import user_logged_in, current_user

from invenio.modules.oauthclient.models import RemoteAccount

from sqlalchemy.sql import exists
from sqlalchemy import and_
from invenio.ext.sqlalchemy import db

def setup_app(app):
    """Attaches functions to before request handler."""
    @user_logged_in.connect_via(app)
    def check_b2access_registration1(*args, **kwargs):
        """Check if the user has logged in with B2Access or not and ask him
        to connect his account to B2Access if it is not already done."""
        has_b2access_account = db.session.query(exists().where(and_(
            RemoteAccount.user_id==current_user.get_id(),
            RemoteAccount.client_id==cfg['UNITY_APP_CREDENTIALS']['consumer_key']
        ))).scalar()
        if not has_b2access_account:
            flash(_('Username and password authentication will soon be ' +
                    'disabled. Please <a href={url}>connect your account to ' +
                    'B2Access </a> for future sign in.')
                .format(url=url_for('oauthclient.login', remote_app='unity')),
                "danger(html_safe)")
        else:
            flash(_('Username and password authentication will soon be ' +
                    'disabled. You will still be able to sign in with your ' +
                    'B2Access account.'),
                "warning(html_safe)")


__all__ = ['setup_app']
