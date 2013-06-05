## This file is part of Invenio.
## Copyright (C) 2010, 2011 CERN.
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

"""
Customise activation e-mail.
"""

from flask import render_template

from invenio.websession_templates import Template as DefaultTemplate
from invenio.config import (CFG_SITE_SECURE_URL,
                            CFG_WEBSESSION_ADDRESS_ACTIVATION_EXPIRE_IN_DAYS,
                            CFG_SITE_LANG)


class Template(DefaultTemplate):

    def tmpl_account_address_activation_email_body(
            self, email, address_activation_key, ip_address, ln=CFG_SITE_LANG):
        """
        The body of the email that sends email address activation cookie
        passwords to users.
        """
        from urllib import urlencode
        ctx = {
            "ip_address": ip_address,
            "email": email,
            "activation_link": "%s/youraccount/access?%s" % (
                CFG_SITE_SECURE_URL,
                urlencode({
                    "ln": ln,
                    "mailcookie": address_activation_key,
                })
            ),
            "days": CFG_WEBSESSION_ADDRESS_ACTIVATION_EXPIRE_IN_DAYS,
        }

        return render_template(
            "websession_account_address_activation_email_body.html",
            **ctx).encode('utf8')
