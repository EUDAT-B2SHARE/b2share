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

import os, os.path, uuid

from flask import current_app, request
from flask.ext.login import current_user
from flask.ext.restful import Resource, abort, reqparse

from werkzeug.datastructures import ImmutableMultiDict

from wtforms.ext.sqlalchemy.orm import model_form

from invenio.ext.restful import require_api_auth
from invenio.modules.editor.models import Bib98x, BibrecBib98x
from invenio.modules.formatter import engine as bibformat_engine

from invenio.b2share.modules.b2deposit.b2share_model import metadata_classes
from invenio.b2share.modules.b2deposit.b2share_model.HTML5ModelConverter \
    import HTML5ModelConverter
from invenio.b2share.modules.b2deposit.b2share_upload_handler \
    import encode_filename, get_extension, create_file_metadata
from invenio.b2share.modules.b2deposit.b2share_marc_handler \
    import get_depositing_files_metadata, create_marc
from invenio.b2share.modules.b2deposit.b2share_deposit_handler \
    import write_marc_to_temp_file, FormWithKey


PAGE_SIZE = 20
MAX_PAGE_SIZE = 100


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
    'uploaded_by':          ('8560_f', False),
    'contact_email':        ('270__m', False),
    'open_access':          ('542__l', False),
    'licence':              ('540__a', False),
    'version':              ('250__a', False),
    'alternate_identifier': ('024__a', False),
}

def read_basic_metadata_field_from_marc(bfo, fieldname):
    if fieldname in basic_fields_meta:
        marctag = basic_fields_meta[fieldname][0]
        multiple = basic_fields_meta[fieldname][1]

        # we need to do additional filtering due to the clash between domain and resource_type
        # they are both encoded as the same marc field
        if fieldname == 'domain':
            ret = [r.lower() for r in bfo.fields(marctag) if r.lower() in metadata_classes()]
            return ret if multiple else ", ".join(ret)
        elif fieldname == 'resource_type':
            ret = [r for r in bfo.fields(marctag) if r.lower() not in metadata_classes()]
            return ret if multiple else ", ".join(ret)
        elif marctag:
            if multiple:
                return bfo.fields(marctag)
            else:
                return bfo.field(marctag)
    return None

def read_domain_specific_metadata_field_from_marc(bfo, fieldname, multiple):
    ret = [fx.get('b') for fx in bfo.fields('690__')
                           if fx.get('a') == fieldname and fx.get('b')]
    return ret if multiple else ", ".join(ret)

def get_domain_metadata(domain_class, fieldset, bfo):
    ret = {}
    for fieldname in fieldset.optional_fields + fieldset.basic_fields:
        field = domain_class.field_args[fieldname]
        multiple = 'cardinality' in field and field['cardinality'] == 'n'
        ret[fieldname] = read_domain_specific_metadata_field_from_marc(bfo, fieldname, multiple)
    return ret

def get_record_details(recid, curr_user_email):
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
        if fieldname == "open_access" and read_basic_metadata_field_from_marc(bfo, fieldname) == "restricted":
            if read_basic_metadata_field_from_marc(bfo, "uploaded_by") != curr_user_email:
                ret['files'] = "RESTRICTED"
                ret[fieldname] = read_basic_metadata_field_from_marc(bfo, fieldname)
        else:
            ret[fieldname] = read_basic_metadata_field_from_marc(bfo, fieldname)

    # add 'PID'
    for fx in bfo.fields('0247_'):
        if fx.get('2') == "PID":
            ret[fx.get('2')] = fx.get('a')

    # add 'domain'
    domain = read_basic_metadata_field_from_marc(bfo, 'domain')
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

pager = reqparse.RequestParser()
pager.add_argument('page_size', type=int, help='Number of items to return')
pager.add_argument('page_offset', type=int, help='Index of the first returned item')

class B2Resource(Resource):
    method_decorators = [require_api_auth()]
    def get(self, oauth, **kwargs): abort(405)
    def post(self, oauth, **kwargs): abort(405)
    def put(self, oauth, **kwargs): abort(405)
    def delete(self, oauth, **kwargs): abort(405)
    def head(self, oauth, **kwargs): abort(405)
    def options(self, oauth, **kwargs): abort(405)
    def patch(self, oauth, **kwargs): abort(405)

class ListRecordsByDomain(B2Resource):
    """
    The resource representing the collection of all records, filtered by domain

    Can only list the available resources,
    use POST to /depositions to create a new one
    """
    def get(self, oauth, domain_name, **kwargs):
        pag = pager.parse_args()
        page_size = pag.get('page_size') or PAGE_SIZE
        page_offset = pag.get('page_offset') or 0
        if page_size > MAX_PAGE_SIZE:
            page_size = MAX_PAGE_SIZE

        # get domain id from domain name
        domain = Bib98x.query.filter_by(value=domain_name).first()
        if domain is None:
            abort(404, status=404,
                  message="Please try a valid domain name: " +
                         ", ".join(metadata_classes().keys()))

        domain_records = BibrecBib98x.query.filter_by(id_bibxxx=domain.id).all()
        record_ids = [record.id_bibrec for record in domain_records]
        curr_user_email = current_user['email']

        record_list = []
        start = page_offset * page_size
        stop = start + page_size
        for record_id in record_ids[start : stop]:
            record_details = get_record_details(record_id, curr_user_email)
            record_list.append(record_details)
        if stop < len(record_ids):
            record_list.append('...') # continuation indicator
        return record_list


class ListRecords(B2Resource):
    """
    The resource representing the collection of all records

    Can only list the available records,
    use POST to /depositions to create a new one
    """
    def get(self, oauth, **kwargs):
        from invenio.legacy.search_engine import perform_request_search
        # from invenio.modules.accounts.models import User

        pag = pager.parse_args()
        page_size = pag.get('page_size') or PAGE_SIZE
        page_offset = pag.get('page_offset') or 0
        if page_size > MAX_PAGE_SIZE:
            page_size = MAX_PAGE_SIZE

        # enumerate all valid ids
        record_ids = perform_request_search(of="id", sf="005")
        curr_user_email = current_user['email']
        record_list = []
        start = page_offset * page_size
        stop = start + page_size
        for record_id in record_ids[start : stop]:
            record_details = get_record_details(record_id, curr_user_email)
            record_list.append(record_details)
        if stop < len(record_ids):
            record_list.append('...') # continuation indicator
        return record_list


class RecordRes(B2Resource):
    """
    A record resource is (for now) immutable, can be read with GET
    """
    def get(self, oauth, record_id, **kwargs):
        curr_user_email = current_user['email']
        record_details = get_record_details(record_id, curr_user_email)
        if not record_details:
            abort(404, message="Deposition not found", status=404)
        return record_details


class ListDepositions(B2Resource):
    """
    The resource representing the active deposits.
    A deposit is mutable and private, while a record is immutable and public
    """
    def get(self, oauth, **kwargs):
        # TODO: ideally we'd be able to list all depositIDs of the current user
        #       but right now we don't know which ones belong to this user
        abort(405)

    def post(self, oauth, **kwargs):
        """
        Creates a new deposition

        Test this with:
        $ curl -v -X POST http://0.0.0.0:4000/api/depositions?access_token=xxx
        should return a new Location URL
        """
        CFG_B2SHARE_UPLOAD_FOLDER = current_app.config.get(
                                "CFG_B2SHARE_UPLOAD_FOLDER")
        deposit_id = uuid.uuid1().hex
        upload_dir = os.path.join(CFG_B2SHARE_UPLOAD_FOLDER, deposit_id)
        os.makedirs(upload_dir)
        location = "/api/deposition/" + deposit_id,
        json_data = {
            'message': "New deposition created",
            'location': "/api/deposition/" + deposit_id,
        }
        return json_data, 201, {'Location' : location} # return location header


class Deposition(B2Resource):
    """
    The resource representing a deposition.
    """
    def get(self, oauth, deposit_id, **kwargs):
        """
        Test this with:
        $ curl -v http://0.0.0.0:4000/api/deposition/DEPOSITION_ID?access_token=xxx
        """
        prefix = '/api/deposition/'+deposit_id
        return {'message':'valid deposition resource',
                'locations': [ prefix + '/files', prefix + '/commit']}

class DepositionFiles(B2Resource):
    """
    The resource representing the list of files in a deposition.
    """
    def check_user(self, deposit_id):
        # TODO: make sure the deposition folder is only readable by its owner
        pass

    def get(self, oauth, deposit_id, **kwargs):
        """
        Get the list of files already uploaded

        Test this with:
        $ curl -v http://0.0.0.0:4000/api/deposition/DEPOSITION_ID/files?access_token=xxx
        should return the list of deposited files
        """
        CFG_B2SHARE_UPLOAD_FOLDER = current_app.config.get(
                                "CFG_B2SHARE_UPLOAD_FOLDER")
        upload_dir = os.path.join(CFG_B2SHARE_UPLOAD_FOLDER, deposit_id)
        if not os.path.exists(upload_dir):
            # don't use abort(404), it adds its own bad error message
            return {'message':'bad deposit_id parameter', 'status':404}, 404
        self.check_user(deposit_id)
        files = [{'name': f['name'], 'size': f['size'] }
                 for f in get_depositing_files_metadata(deposit_id)]
        return files

    def post(self, oauth, deposit_id, **kwargs):
        """
        Adds a new deposition file

        Test this with:
        $ curl -v -X POST -F file=@TestFileToBeUploaded.txt
          http://0.0.0.0:4000/api/deposition/DEPOSITION_ID/files?access_token=xxx
        should return the newly deposited files
        """
        CFG_B2SHARE_UPLOAD_FOLDER = current_app.config.get(
                                "CFG_B2SHARE_UPLOAD_FOLDER")
        upload_dir = os.path.join(CFG_B2SHARE_UPLOAD_FOLDER, deposit_id)
        if not os.path.exists(upload_dir):
            # don't use abort(404), it adds its own bad error message
            return {'message':'bad deposit_id parameter', 'status':404}, 404

        self.check_user(deposit_id)

        file_names = []
        for f in request.files.values():
            safename, md5 = encode_filename(f.filename)
            file_unique_name = safename + "_" + md5 + get_extension(safename)
            file_path = os.path.join(upload_dir, file_unique_name)
            f.save(file_path)
            create_file_metadata(upload_dir, f.filename, file_unique_name, file_path)
            file_names.append({'name':f.filename})
        return {'message':'File(s) saved', 'files':file_names}

class DepositionCommit(B2Resource):
    """
    The resource representing a deposition commit action.
    By POSTing valid metadata here the deposition is transformed into a record
    """
    def post(self, oauth, deposit_id, **kwargs):
        """
        Creates a new deposition

        Test this with:
        $ curl -v -X POST -H "Content-Type: application/json"
          -d '{"domain":"generic", "title":"REST Test Title", "description":"REST Test Description"}'
          http://0.0.0.0:4000/api/deposition/DEPOSITION_ID/commit\?access_token\=xxx
        """
        CFG_B2SHARE_UPLOAD_FOLDER = current_app.config.get(
                                "CFG_B2SHARE_UPLOAD_FOLDER")
        upload_dir = os.path.join(CFG_B2SHARE_UPLOAD_FOLDER, deposit_id)
        if not os.path.exists(upload_dir):
            # don't use abort(404), it adds its own bad error message
            return {'message':'bad deposit_id parameter', 'status':404}, 404
        if not os.listdir(upload_dir):
            return {'message':'no files: add files to this deposition first', 'status':400}, 400

        try:
            form = request.get_json()
        except:
            return {'message':'Invalid POST data', 'status':400}, 400

        domain = form.get('domain', '').lower()
        if domain in metadata_classes():
            metaclass = metadata_classes()[domain]
            meta = metaclass()
        else:
            domains = ", ".join(metadata_classes().keys())
            json_data = {
                'message': 'Invalid domain. The submitted metadata must '+\
                            'contain a valid "domain" field. Valid domains '+\
                            'are: '+ domains,
                'status': 400,
            }
            return json_data, 400

        if 'open_access' not in form:
            return {'message':'open_access boolean field required', 'status':400}, 400
        if not form['open_access'] or form['open_access'] == 'restricted':
            del form['open_access'] # action required by the b2share_marc_handler

        if not form.get('language'):
            form['language'] = meta.language_default

        form = ImmutableMultiDict(form)

        MetaForm = model_form(meta.__class__, base_class=FormWithKey,
                              exclude=['submission', 'submission_type'],
                              field_args=meta.field_args,
                              converter=HTML5ModelConverter())

        meta_form = MetaForm(form, meta, csrf_enabled=False)

        if meta_form.validate_on_submit():
            recid, marc = create_marc(form, deposit_id, current_user['email'], meta)
            tmp_file = write_marc_to_temp_file(marc)
            # all usual tasks have priority 0; we want the bibuploads to run first
            from invenio.legacy.bibsched.bibtask import task_low_level_submission
            task_low_level_submission('bibupload', 'webdeposit', '--priority', '1', '-r', tmp_file)

            #TODO: remove the existing deposition folder?; the user can now
            #      repeatedly create records with the same deposition

            location = "/api/record/%d" % (recid,)
            json_data = {
                'message': "New record submitted for processing",
                'location': "/api/record/%d" % (recid,)
            }
            return json_data, 201, {'Location':location} # return location header
        else:
            fields = {}
            for (fname, field) in meta.field_args.iteritems():
                if not field.get('hidden'):
                    fields[fname] = { 'description' : field.get('description') }
                    if self.is_required_field(metaclass, fname):
                        fields[fname]['required'] = True
                    if field.get('cardinality') == 'n':
                        fields[fname]['multiple'] = True
                    if field.get('data_source'):
                        fields[fname]['options'] = field.get('data_source')

            json_data = {
                'message': 'Invalid metadata, please review the required fields',
                'status': 400,
                'fields': fields,
            }
            return json_data, 400

    def is_required_field(self, cls, propname):
        from sqlalchemy.orm import class_mapper
        import sqlalchemy
        for prop in class_mapper(cls).iterate_properties:
            if isinstance(prop, sqlalchemy.orm.ColumnProperty) and prop.key == propname:
                for col in prop.columns:
                    if col.nullable == False:
                        return True
        return False

#
# Register API resources
#


def setup_app(app, api):
    api.add_resource(ListRecords, '/api/records/')
    api.add_resource(ListRecordsByDomain, '/api/records/<string:domain_name>')
    api.add_resource(RecordRes, '/api/record/<int:record_id>')

    api.add_resource(ListDepositions, '/api/depositions/')
    api.add_resource(Deposition, '/api/deposition/<string:deposit_id>')
    api.add_resource(DepositionFiles, '/api/deposition/<string:deposit_id>/files')
    api.add_resource(DepositionCommit, '/api/deposition/<string:deposit_id>/commit')
