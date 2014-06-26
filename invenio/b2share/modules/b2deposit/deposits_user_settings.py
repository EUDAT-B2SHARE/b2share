# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2013 CERN.
##
## Invenio is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## Invenio is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Invenio; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""Deposits User Settings"""

# Flask
from flask import url_for
from invenio.jinja2utils import render_template_to_string
from invenio.webinterface_handler_flask_utils import _
from invenio.webuser_flask import current_user
from invenio.settings import Settings, UserSettingsStorage

# Related models
from invenio.websession_model import User
from invenio.search_engine import perform_request_search

class DepositsSettings(Settings):

    keys = []
    #form_builder = WebBasketUserSettingsForm
    storage_builder = UserSettingsStorage

    def __init__(self):
        super(DepositsSettings, self).__init__()
        self.icon = 'folder-open'
        self.title = _('Deposits')
        try:
            user = User.query.get(current_user.get_id())
            email = user.email
            email_field = "8560_"
            self.view = url_for('search.search', f=email_field, p=email)
        except:
            self.view = ''

    def widget(self):
        user = User.query.get(current_user.get_id())
        email = user.email
        email_field = "8560_"
        deposit_count = len(perform_request_search(f=email_field, p=email, of="id"))

        return render_template_to_string('deposits_user_settings.html',
            email=email, email_field=email_field, deposit_count=deposit_count)

    widget.size = 4

    @property
    def is_authorized(self):
        return current_user.is_authenticated()

## Compulsory plugin interface
settings = DepositsSettings
