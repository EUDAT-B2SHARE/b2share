## -*- coding: utf-8 -*-
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

############### common

# hack: lodash exports _, which is later hijacked by invenio
# we run lodash before anything else and save the exported _
b2s_pre_almond_init_js = Bundle(
    "vendors/lodash/dist/lodash.js",
    "js/lodash-fix.js",
    output="b2s_pre_almond_init.js",
    weight=-1,
)

b2s_common_css = Bundle(
    "css/b2s-common.css",
    output="b2s_common.css",
    filters="cleancss",
    weight=60,
)

############### deposit

b2s_deposit_js = Bundle(
    "vendors/bootstrap-switch/dist/js/bootstrap-switch.js",
    "vendors/bootstrap-multiselect/dist/js/bootstrap-multiselect.js",
    "vendors/plupload/js/plupload.full.min.js",
    "vendors/typeahead.js/dist/typeahead.jquery.js",
    "js/lodash-fix.js",
    "vendors/lindat-license-selector/license-selector.min.js",
    "js/b2s-deposit.js",
    output="b2s_deposit.js",
    filters="requirejs",
    bower={
        "bootstrap-switch": "3.0.2",
        "bootstrap-multiselect": "0.9.10",
        "typeahead.js": "0.10.4",
        "plupload": "latest",
        "lindat-license-selector": "0.0.3",
    },
    weight=60,
)

b2s_deposit_editor_js = Bundle(
    "vendors/bootstrap-switch/dist/js/bootstrap-switch.js",
    "vendors/bootstrap-multiselect/dist/js/bootstrap-multiselect.js",
    "vendors/typeahead.js/dist/typeahead.jquery.js",
    "js/lodash-fix.js",
    "vendors/lindat-license-selector/license-selector.min.js",
    "js/b2s-deposit-editor.js",
    output="b2s_deposit_editor.js",
    filters="requirejs",
    bower={
        "bootstrap-switch": "3.0.2",
        "bootstrap-multiselect": "0.9.10",
        "typeahead.js": "0.10.4",
        "lindat-license-selector": "0.0.3",
    },
    weight=60,
)

b2s_deposit_css = Bundle(
    "vendors/bootstrap-switch/dist/css/bootstrap3/bootstrap-switch.css",
    "vendors/bootstrap-multiselect/dist/css/bootstrap-multiselect.css",
    "vendors/typeahead.js-bootstrap3.less/typeahead.css",
    "vendors/lindat-license-selector/license-selector.min.css",
    "css/b2s-deposit.css",
    output="b2s_deposit.css",
    filters="cleancss",
    weight=60,
)

############### record

b2s_record_css = Bundle(
    "css/b2s-record.css",
    output="b2s_record.css",
    filters="cleancss",
    weight=60,
)

############### abuse and data requests

b2s_abuse_css = Bundle(
    "css/b2s-abuse.css",
    output="b2s_abuse.css",
    filters="cleancss",
    weight=60,
)

b2s_abuse_js = Bundle(
    "js/b2s-abuse.js",
    output="b2s_abuse.js",
    filters="uglifyjs",
    weight=60,
)
