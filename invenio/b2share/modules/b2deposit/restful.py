# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2013, 2014 CERN.
#
# Invenio is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

from __future__ import absolute_import

import json

from flask import current_app, Response
from flask.ext.login import current_user
from flask.ext.restful import Resource, abort

from invenio.ext.restful import require_api_auth, require_header
from invenio.modules.editor.models import Bib98x, BibrecBib98x
from invenio.modules.formatter import engine as bibformat_engine

from invenio.b2share.modules.b2deposit.b2share_model import metadata_classes


MAX_PAGE_SIZE = 20


# =========
# Mix-ins
# =========
deposit_decorators = [
    require_api_auth(),
]


###############################################################################
# Conversion table for the set of basic fields of a record,
# as expressed in the b2share_model/metdata/metadata.py:
#
#     1. the field name, spelled as in the metadata model
#     2. their encoding as marc fields in the database,
#     3. their multiplicity in the database (True of False)
#
#    FIELD_NAME              MARC      MULTIPLE
basic_fields_meta = {
    'creator':              ('100__a', True),
    'title':                ('245__a', False),
    'description':          ('520__a', False),
    'keywords':             ('6531_a', True),
    'contributors':         ('700__a', True),
    'domain':               ('980__a', False), #\ same marctag
    'resource_type':        ('980__a', True),  #/ same marctag
    'publication_date':     ('260__c', False),
    'contact_email':        ('270__m', False),
    'open_access':          ('542__l', False),
    'licence':              ('540__a', False),
    'version':              ('250__a', False),
    'alternate_identifier': ('024__a', False),
}

def read_basic_medata_field_from_marc(bfo, fieldname):
    if fieldname in basic_fields_meta:
        marctag = basic_fields_meta[fieldname][0]
        multiple = basic_fields_meta[fieldname][1]
        if marctag == '980__a':
            # duplicated marc tag, serves as domain specifier
            #   and also as resource_type specifier
            ret = bfo.fields(marctag)
            if fieldname == 'domain':
                ret = [r.lower() for r in ret if r.lower() in metadata_classes()]
            else:
                ret = [r for r in ret if r.lower() not in metadata_classes()]
            return ret if multiple else ", ".join(ret)
        elif marctag:
            if multiple:
                return bfo.fields(marctag)
            else:
                return bfo.field(marctag)
    return None

def read_domain_specific_medata_field_from_marc(bfo, fieldname, multiple):
    ret = [fx.get('b') for fx in bfo.fields('690__')
                           if fx.get('a') == fieldname and fx.get('b')]
    return ret if multiple else ", ".join(ret)

def get_domain_metadata(domain_class, fieldset, bfo):
    ret = {}
    for fieldname in fieldset.optional_fields + fieldset.basic_fields:
        field = domain_class.field_args[fieldname]
        multiple = 'cardinality' in field and field['cardinality'] == 'n'
        ret[fieldname] = read_domain_specific_medata_field_from_marc(bfo, fieldname, multiple)
    return ret

def get_record_details(recid):
    from invenio.legacy.bibdocfile.api import BibRecDocs
    try:
        recdocs = BibRecDocs(recid)
    except:
        current_app.logger.error("REST API: Error while building BibRecDocs for record %d" % (recid,))
        return []

    latest_files = recdocs.list_latest_files()
    if len(latest_files) == 0:
        current_app.logger.error("REST API: BibRecDocs reports 0 files for record %d" % (recid,))
        return []

    # bibformat uses get_record, usually is one db hit per object; should be fastest
    bfo = bibformat_engine.BibFormatObject(recid)

    # first put the recordID and list of files
    ret = {
        'recordID': recid,
        'files': [{
                        'name': afile.get_full_name().decode('utf-8'),
                        'size': afile.get_size(),
                        'url': afile.get_full_url(),
                  } for afile in latest_files ],
    }
 
    # add basic metadata fields
    for fieldname in basic_fields_meta:
        ret[fieldname] = read_basic_medata_field_from_marc(bfo, fieldname)

    # add 'PID'
    for fx in bfo.fields('0247_'):
        if fx.get('2') == "PID":
            ret[fx.get('2')] = fx.get('a')

    # add 'domain'
    domain = read_basic_medata_field_from_marc(bfo, 'domain')
    ret['domain'] = domain

    # add domain-specific metadata fields
    if domain not in metadata_classes():
        current_app.logger.error("Bad domain metadata class for record %d" % (recid,))
    else:
        domain_class = metadata_classes()[domain]()
        for fieldset in domain_class.fieldsets:
            if fieldset.name != 'Generic':
                ret['domain_metadata'] = get_domain_metadata(domain_class, fieldset, bfo)

    return ret

# =========
# Resources
# =========
class DepositionDomains(Resource):
    """
    Collection of depositions: specific Domain
    """
    method_decorators = deposit_decorators

    def get(self, oauth, domain_name, **kwargs):
        """
        List all deposits for a specific domain

        """

        if len(kwargs) == 0:
            page_size = 5
            page_offset = 0
        elif len(kwargs) == 1:
            if kwargs['page_size'] > MAX_PAGE_SIZE:
                page_size = MAX_PAGE_SIZE
            else:
                page_size = kwargs['page_size']
            page_offset = 0
        elif len(kwargs) == 2:
            if kwargs['page_size'] > MAX_PAGE_SIZE:
                page_size = MAX_PAGE_SIZE
            else:
                page_size = kwargs['page_size']
            page_offset = kwargs['page_offset']

        # get domain id from domain name
        domain = Bib98x.query.filter_by(value=domain_name).first()
        if domain is None:
            abort(404, status=404,
                  message="Please try a valid domain name: " +
                         ", ".join(metadata_classes().keys()))

        domain_records = BibrecBib98x.query.filter_by(id_bibxxx=domain.id).all()
        record_ids = [record.id_bibrec for record in domain_records]

        record_list = []
        for record_id in record_ids[page_offset * page_size:page_offset * page_size + page_size]:
            record_details = get_record_details(record_id)
            record_list.append(record_details)

        return record_list

    @require_header('Content-Type', 'application/json')
    def post(self, oauth):
        """
        Create a new deposition
        """
        abort(405)

    def put(self, oauth):
        abort(405)

    def delete(self, oauth):
        abort(405)

    def head(self, oauth):
        abort(405)

    def options(self, oauth):
        abort(405)

    def patch(self, oauth):
        abort(405)


class DepositionListRecord(Resource):
    """
    Collection of depositions: specific user
    """
    method_decorators = deposit_decorators

    def get(self, oauth, **kwargs):
        """
        List depositions

        """
        from invenio.legacy.search_engine import perform_request_search
        # from invenio.modules.accounts.models import User

        if len(kwargs) == 0:
            page_size = 5
            page_offset = 0
        elif len(kwargs) == 1:
            if kwargs['page_size'] > MAX_PAGE_SIZE:
                page_size = MAX_PAGE_SIZE
            else:
                page_size = kwargs['page_size']
            page_offset = 0
        elif len(kwargs) == 2:
            if kwargs['page_size'] > MAX_PAGE_SIZE:
                page_size = MAX_PAGE_SIZE
            else:
                page_size = kwargs['page_size']
            page_offset = kwargs['page_offset']

        email_field = "8560_"
        email = current_user['email']
        record_ids = perform_request_search(f=email_field, p=email, of="id")
        record_list = []

        for record_id in record_ids[page_offset * page_size:page_offset * page_size + page_size]:
            record_details = get_record_details(record_id)
            record_list.append(record_details)
        return record_list

    def post(self, oauth):
        """
        Create a new deposition
        """
        pass

    def put(self, oauth):
        abort(405)

    def delete(self, oauth):
        abort(405)

    def head(self, oauth):
        abort(405)

    def options(self, oauth):
        abort(405)

    def patch(self, oauth):
        abort(405)


class DepositionRecord(Resource):
    """
    Deposition item
    """
    method_decorators = deposit_decorators

    def get(self, oauth, record_id):
        """
        Retrieve requested record

        """
        record_details = get_record_details(record_id)
        if not record_details:
            abort(404, message="Deposition not found", status=404)
        return record_details

    def post(self, oauth):
        """
        Create a new deposition
        """
        pass

    def put(self, oauth):
        abort(405)

    def delete(self, oauth):
        abort(405)

    def head(self, oauth):
        abort(405)

    def options(self, oauth):
        abort(405)

    def patch(self, oauth):
        abort(405)


#
# Register API resources
#


def setup_app(app, api):
    api.add_resource(
        DepositionDomains,
        '/api/depositions/<string:domain_name>',
        '/api/depositions/<string:domain_name>/<int:page_size>',
        '/api/depositions/<string:domain_name>/<int:page_size>/<int:page_offset>',
    )
    api.add_resource(
        DepositionListRecord,
        '/api/depositions/',
        '/api/depositions/<int:page_size>/',
        '/api/depositions/<int:page_size>/<int:page_offset>',
    )
    api.add_resource(
        DepositionRecord,
        '/api/deposit/<int:record_id>',
    )
