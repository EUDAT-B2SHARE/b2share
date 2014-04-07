## This file is part of SimpleStore.
## Copyright (C) 2013 EPCC, The University of Edinburgh.
##
## SimpleStore is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## SimpleStore is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with SimpleStore; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

import os
from datetime import datetime
import hashlib
import pickle

from invenio.dbquery import run_sql
from invenio.bibrecord import record_add_field, record_xml_output
from invenio.config import (CFG_SIMPLESTORE_UPLOAD_FOLDER, CFG_SITE_NAME,
                            CFG_SITE_SECURE_URL)
from invenio.simplestore_epic import createHandle
from flask import current_app
from werkzeug.exceptions import HTTPException
from invenio.simplestore_model import metadata_classes
from invenio.htmlutils import remove_html_markup

def add_basic_fields(rec, form, email):
    """
    Adds the basic fields from the form. Note that these fields are mapped
    to specific MARC fields. For information on the fields see the www.loc.gov
    website. For example http://www.loc.gov/marc/bibliographic/bd260.html
    contains information on field 260 for publication data.
    """
    # why aren't subfields a dictionary?!
    try:
        if form['title']:
            record_add_field(rec, '245', subfields=[('a', remove_html_markup(form['title']))])

        if form['creator']:        
            fields = form.getlist('creator')
            for f in fields:
                if f and not f.isspace():
                    record_add_field(rec, '100', subfields=[('a', remove_html_markup(f.strip()))])
            

        if form['domain']:
            record_add_field(rec, '980', subfields=[('a', remove_html_markup(form['domain']))])
        pubfields = []
        if form['publisher']:
            pubfields.append(('b', remove_html_markup(form['publisher'])))
        if form.get('publication_date'):
            pubfields.append(('c', remove_html_markup(form['publication_date'])))
        if pubfields:
            record_add_field(rec, '260', subfields=pubfields)
        record_add_field(rec, '856', ind1='0', subfields=[('f', email)])

        if 'open_access' in form:
            record_add_field(rec, '542', subfields=[('l', 'open')])
        else:
            record_add_field(rec, '542', subfields=[('l', 'restricted')])

        if form['licence']:
            record_add_field(rec, '540', subfields=[('a', remove_html_markup(form['licence']))])
        record_add_field(rec, '520', subfields=[('a', remove_html_markup(form['description']))])

        if form['tags']:
            for kw in form['tags'].split(','):
                if kw and not kw.isspace():
                    record_add_field(rec, '653',
                                 ind1='1',
                                 subfields=[('a', remove_html_markup(kw.strip()))])

        if form['contributors']:
            fields = form.getlist('contributors')
            for f in fields:
                if f and not f.isspace():
                    record_add_field(rec, '700', subfields=[('a', remove_html_markup(f.strip()))])

        record_add_field(rec, '546', subfields=[('a', remove_html_markup(form['language']))])

        # copying zenodo here, but I don't think 980 is the right MARC field
        if form['resource_type']:
            record_add_field(rec, '980', subfields=[('a', remove_html_markup(form['resource_type']))])

        if form['alternate_identifier']:
            record_add_field(rec, '024',
                             subfields=[('a', remove_html_markup(form['alternate_identifier']))])

        if form['version']:
            record_add_field(rec, '250', subfields=[('a', remove_html_markup(form['version']))])
        record_add_field(rec, '264',
                         subfields=[('b', CFG_SITE_NAME),
                                    ('c', str(datetime.utcnow()) + " UTC")])
    except Exception as e:
        current_app.logger.error(e)
        raise

def create_recid():
    """
    Uses the DB to get a record id for the submission.
    """
    return run_sql("INSERT INTO bibrec(creation_date, modification_date) "
                   "values(NOW(), NOW())")


def add_file_info(rec, form, email, sub_id, recid):
    """
    Adds the path to the file and access rights to ther record.
    """
    upload_dir = os.path.join(CFG_SIMPLESTORE_UPLOAD_FOLDER, sub_id)
    files = os.listdir(upload_dir)
    if 'open_access' in form:
        fft_status = 'firerole: allow any\n'
    else:
        fft_status = 'firerole: allow email "{0}"\ndeny all'.format(
            email)
    for f in files:
        path = os.path.join(upload_dir, f)
        if f.startswith('metadata_'):
            # we do not want to do load file metadata into Invenio as files, will extract into MARC fields
            continue
        # load corresponding metadata file
        metadata = {}
        metadata_filename = os.path.join(upload_dir, 'metadata_' + f)
        if os.path.isfile(metadata_filename):
            # expecting to load a dict with the following structure: dict(name=name, file=file_path, size=size)
            metadata = pickle.load(open(metadata_filename, 'rb'))
        else:
            current_app.logger.error('Submitted file \'%s\' is missing metadata file, using default' % f)
            metadata = dict(name=f, file=path, size=str(os.path.getsize(path)))

        record_add_field(rec, 'FFT',
                         subfields=[('a', path),
                         ('n', metadata['name']), # name of the file
                         #('t', 'Type'), # TODO
                         # unfortunately s is used for a timestamp, not file size
                         #('s', 'timestamp'), # s is a timestamp
                         #('w', str(metadata['size'])), # size should be derived automatically, 
                         #                              # but storing it into 'document_moreinfo' field
                         ('r', fft_status)])

        #seems to be impossible to add file size data, thought this would work
        url = "{0}/record/{1}/files/{2}".format(CFG_SITE_SECURE_URL, recid, f)
        record_add_field(rec, '856', ind1='4',
                         subfields=[('u', url),
                                    ('s', str(os.path.getsize(path))),
                                    ('y',metadata['name'])])


def add_domain_fields(rec, form):
    """
    Adds a domain specific fields. These are just added as name value pairs
    to field 690.
    """

    domain = form['domain'].lower()
    if domain in metadata_classes:
        meta = metadata_classes[domain]()
    else:
        #no domain stuff
        return

    for fs in meta.fieldsets:
        if fs.name != 'Generic':  # TODO: this is brittle; get from somewhere
            for k in (fs.optional_fields + fs.basic_fields):                
                if form[k]:
                    fields = form.getlist(k)
                    for f in fields:
                        if f and not f.isspace():
                            record_add_field(rec, '690',
                                     subfields=[('a', k), ('b', f)])
 

def add_epic_pid(rec, recid, checksum):
    """ Adds EPIC PID to the record. If registration fails, can
    also fail the request if CFG_FAIL_ON_MISSING_PID is set to True"""
    location = CFG_SITE_SECURE_URL + '/record/' + str(recid)
    try:
        pid = createHandle(location, checksum)
        record_add_field(rec, '024', ind1='7',
                         subfields=[('2', 'PID'), ('a', pid)])
    except HTTPException as e:
        # If CFG_FAIL_ON_MISSING_PID is not found in invenio-local.conf,
        # default is to assume False
        try:
            from config import CFG_FAIL_ON_MISSING_PID
            fail = bool(CFG_FAIL_ON_MISSING_PID)
        except ImportError:
            fail = False

        current_app.logger.error(
            "Unable to obtain PID from EPIC server {0} {1}: {2}".
            format(e.code, e.name, e))
        if fail:
            raise e


def create_marc(form, sub_id, email):
    """
    Generates MARC data used by Invenio from the filled out form, then
    submits it to the Invenio system.
    """
    rec = {}
    recid = create_recid()
    record_add_field(rec, '001', controlfield_value=str(recid))
    add_basic_fields(rec, form, email)
    add_domain_fields(rec, form)
    add_file_info(rec, form, email, sub_id, recid)
    checksum = create_checksum(rec, sub_id)
    add_epic_pid(rec, recid, checksum)
    marc = record_xml_output(rec)

    return recid, marc


def create_checksum(rec, sub_id, buffersize=64 * 1024):
    """
    Creates a checksum of all the files in the record, and adds it
    to the MARC.
    Returns: checksum as a hex string
    """
    sha = hashlib.sha256()
    upload_dir = os.path.join(CFG_SIMPLESTORE_UPLOAD_FOLDER, sub_id)
    files = sorted(os.listdir(upload_dir))
    for f in files:
        filepath = os.path.join(upload_dir, f)
        with open(filepath, 'rb', buffering=0) as fp:
            while True:
                block = fp.read(buffersize)
                if not block:
                    break
                sha.update(block)
    cs = sha.hexdigest()
    record_add_field(rec, '024', ind1='7',
                     subfields=[('2', 'checksum'), ('a', cs)])
    return cs
