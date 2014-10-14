# -*- coding: utf-8 -*-
##
## This file is part of B2SHARE.
## Copyright (C) 2013 EPCC, The University of Edinburgh.
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

############### css

b2s_common_css = Bundle(
    "css/b2s-common.css",
    output="b2s_common.css",
    filters="cleancss",
    weight=50,
)

b2s_record_css = Bundle(
    "css/b2s-record.css",
    output="b2s_record.css",
    filters="cleancss",
    weight=50,
)

b2s_abuse_css = Bundle(
    "css/b2s-abuse.css",
    output="b2s_abuse.css",
    filters="cleancss",
    weight=50,
)

b2s_deposit_css = Bundle(
    "css/b2s-deposit.css",
    output="b2s_deposit.css",
    filters="cleancss",
    weight=50,
)

############### javascript

b2s_abuse_js = Bundle(
    "js/b2s-abuse.js",
    output="b2s_abuse.js",
    filters="uglifyjs",
    weight=50,
)

b2s_deposit_js = Bundle(
    "js/b2s-deposit.js",
    output="b2s_deposit.js",
    filters="uglifyjs",
    weight=50,
)

# b2s_typeahead_js = Bundle(
#     "js/websearch_typeahead.js",
#     output="b2s_typeahead.js",
#     filters="uglifyjs",
#     weight=50,
# )
