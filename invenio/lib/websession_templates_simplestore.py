## This file is part of Invenio.
## Copyright (C) 2010, 2011 CERN.
## Portions Copyright (C) 2013 EPCC, The University of Edinburgh.
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
from urllib import urlencode

from invenio.messages import gettext_set_language
from invenio.websession_templates import Template as DefaultTemplate
from invenio.config import (CFG_SITE_SECURE_URL,
                            CFG_WEBSESSION_ADDRESS_ACTIVATION_EXPIRE_IN_DAYS,
                            CFG_SITE_LANG, CFG_SITE_NAME, CFG_SITE_NAME_INTL,
                            CFG_WEBSESSION_RESET_PASSWORD_EXPIRE_IN_DAYS)


class Template(DefaultTemplate):

    def tmpl_account_address_activation_email_body(
            self, email, address_activation_key, ip_address, ln=CFG_SITE_LANG):
        """
        The body of the email that sends email address activation cookie
        passwords to users.
        """
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

    def tmpl_lost_password_form(self, ln):
        """
        Displays a form for the user to ask for his password sent by email.

        Parameters:

          - 'ln' *string* - The language to display the interface in

          - 'msg' *string* - Explicative message on top of the form.
        """

        # load the right message language
        out = "<p>" + "Please enter the email address that you used to sign up to %s. We will send a password reset link to this address." % CFG_SITE_NAME_INTL[ln] + "</p>"

        out += """
          <blockquote>
          <form  method="post" action="../youraccount/send_email">
          <table>
                <tr>
              <td align="right"><strong><label for="p_email">%(email)s:</label></strong></td>
              <td><input type="text" size="25" name="p_email" id="p_email" value="" />
                  <input type="hidden" name="ln" value="%(ln)s" />
                  <input type="hidden" name="action" value="lost" />
              </td>
            </tr>
            <tr><td>&nbsp;</td>
              <td><input class="formbutton" type="submit" value="%(send)s" /></td>
            </tr>
          </table>

          </form>
          </blockquote>
          """ % {'ln': ln, 'email': "Email address",
                 'send': "Send password reset link"}

        return out

    def tmpl_account_reset_password_email_body(self, email, reset_key, ip_address, ln=CFG_SITE_LANG):
        """
        The body of the email that sends lost internal account
        passwords to users.
        """

        _ = gettext_set_language(ln)

        out = """
%(intro)s

%(intro2)s

%(link)s

%(outro)s

%(outro2)s""" % {
            'intro': _("Somebody (possibly you) "
                       "has asked for a password reset at %(x_sitename)s\nfor "
                       "the account \"%(x_email)s\"."
                       % {
                           'x_sitename': CFG_SITE_NAME_INTL.get(ln, CFG_SITE_NAME),
                           'x_email': email,
                           'x_ip_address': ip_address,
                       }
                       ),
            'intro2': _("If you want to reset the password for this account, please go to:"),
            'link': "%s/youraccount/access?%s" %
            (CFG_SITE_SECURE_URL, urlencode({
                'ln': ln,
                'mailcookie': reset_key})),
            'outro': _("in order to confirm the validity of this request."),
            'outro2': _("Please note that this URL will remain valid for about %(days)s days only.") % {'days': CFG_WEBSESSION_RESET_PASSWORD_EXPIRE_IN_DAYS},
        }
        return out

    def tmpl_reset_password_form(self, ln, email, reset_key, msg=''):
        """Display a form to reset the password."""

        _ = gettext_set_language(ln)

        out = ""
        out = "<p>%s</p>" % _("Your request is valid. Please set the new "
                              "desired password in the following form.")
        if msg:
            out += """<p class='warning'>%s</p>""" % msg
        out += """
<form method="post" action="../youraccount/resetpassword?ln=%(ln)s">
<input type="hidden" name="k" value="%(reset_key)s" />
<input type="hidden" name="e" value="%(email)s" />
<input type="hidden" name="reset" value="1" />
<table>
<tr><td align="right"><strong>%(set_password_for)s</strong>:</td><td><em>%(email)s</em></td></tr>
<tr><td align="right"><strong><label for="password">%(type_new_password)s:</label></strong></td>
<td><input type="password" name="password" id="password" value="" /></td></tr>
<tr><td align="right"><strong><label for="password2">%(type_it_again)s:</label></strong></td>
<td><input type="password" name="password2" id="password2" value="" /></td></tr>
<tr><td align="center" colspan="2">
<input class="formbutton" type="submit" name="action" value="%(set_new_password)s" />
</td></tr>
</table>
</form>""" % {
            'ln': ln,
            'reset_key': reset_key,
            'email': email,
            'set_password_for': _('Set a new password for'),
            'type_new_password': _('Type the new password'),
            'type_it_again': _('Type again the new password'),
            'set_new_password': _('Set the new password')
        }
        return out
