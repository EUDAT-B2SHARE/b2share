## -*- coding: utf-8 -*-
##
## This file is part of B2SHARE.
## Copyright (C) 2015, CERN.
##
## B2SHARE is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## B2SHARE is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with B2SHARE; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""B2SHARE bundles."""

from invenio.ext.assets import Bundle

b2s_login_css = Bundle(
    "css/accounts/b2s-accounts.css",
    output="b2s_accounts.css",
    filters="cleancss",
    weight=60,
)
