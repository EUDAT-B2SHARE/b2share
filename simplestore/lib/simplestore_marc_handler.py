import os
from datetime import datetime
import hashlib

from invenio.dbquery import run_sql
from invenio.bibrecord import record_add_field, record_xml_output
from invenio.config import (CFG_SIMPLESTORE_UPLOAD_FOLDER, CFG_SITE_NAME,
                            CFG_SITE_SECURE_URL)

from flask import current_app
from werkzeug.exceptions import HTTPException

from invenio.simplestore_epic import createHandle
from invenio.simplestore_model.model import SubmissionMetadata
from invenio.simplestore_model import metadata_classes


def add_basic_fields(rec, form, email):
    """
    Adds the basic fields from the form. Note that these fields are mapped
    to specific MARC fields. For information on the fields see the www.loc.gov
    website. For example http://www.loc.gov/marc/bibliographic/bd260.html
    contains information on field 260 for publication data.
    """
    # why aren't subfields a dictionary?!
    if form['title']:
        record_add_field(rec, '245', subfields=[('a', form['title'])])

    if form['creator']:
        record_add_field(rec, '100', subfields=[('a', form['creator'])])

    if form['domain']:
        record_add_field(rec, '980', subfields=[('a', form['domain'])])

    pubfields = []
    if form['publisher']:
        pubfields.append(('b', form['publisher']))

    if form['publication_date']:
        pubfields.append(('c', form['publication_date']))

    if pubfields:
        record_add_field(rec, '260', subfields=pubfields)

    record_add_field(rec, '856', ind1='0', subfields=[('f', email)])

    if 'open_access' in form:
        record_add_field(rec, '542', subfields=[('l', 'open')])
    else:
        record_add_field(rec, '542', subfields=[('l', 'restricted')])

    if form['licence']:
        record_add_field(rec, '540', subfields=[('a', form['licence'])])

    record_add_field(rec, '520', subfields=[('a', form['description'])])

    if form['tags']:
        for kw in form['tags'].split(','):
            record_add_field(rec, '653',
                             ind1='1',
                             subfields=[('a', kw.strip())])

    if form['contributors']:
        for kw in form['contributors'].split(';'):
            record_add_field(rec, '700', subfields=[('a', kw.strip())])

    if form['language']:
        record_add_field(rec, '546', subfields=[('a', form['language'])])

    # copying zenodo here, but I don't think 980 is the right MARC field
    if form['resource_type']:
        record_add_field(rec, '980', subfields=[('a', form['resource_type'])])

    if form['alternate_identifier']:
        record_add_field(rec, '024',
                         subfields=[('a', form['alternate_identifier'])])

    if form['version']:
        record_add_field(rec, '250', subfields=[('a', form['version'])])

    record_add_field(rec, '264',
                     subfields=[('b', CFG_SITE_NAME),
                                ('c', str(datetime.utcnow()) + " UTC")])


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
        record_add_field(rec, 'FFT',
                         subfields=[('a', path),
                         #('d', 'some description') # TODO
                         #('t', 'Type'), # TODO
                         # unfortunately s is used for a timestamp, not file size
                         #('s', str(os.path.getsize(path))),
                         ('r', fft_status)])

        #seems to be impossible to add file size data, thought this would work
        url = "{0}/record/{1}/files/{2}".format(CFG_SITE_SECURE_URL, recid, f)
        record_add_field(rec, '856', ind1='4',
                         subfields=[('u', url),
                                    ('s', str(os.path.getsize(path)))])


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
                    record_add_field(rec, '690',
                                     subfields=[('a', k), ('b', form[k])])


def add_epic_pid(rec, recid, checksum):
    """ Adds EPIC PID to the record. If registration fails, can 
    also fail the request if CFG_FAIL_ON_MISSING_PID is set to True"""
    location = CFG_SITE_SECURE_URL + '/record/' + str(recid)
    try:
        pid = createHandle(location, checksum)
        record_add_field(rec, '024', ind1='7',
                         subfields = [('2', 'PID'), ('a', pid)])
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


def create_checksum(rec, sub_id, buffersize=64*1024):
    """
    Creates a checksum of all the files in the record, and adds it
    to the MARC.
    Returns: checksum as a hex string
    """
    buffer = bytearray(buffersize)
    sha = hashlib.sha256()
    upload_dir = os.path.join(CFG_SIMPLESTORE_UPLOAD_FOLDER, sub_id)
    files = sorted(os.listdir(upload_dir))
    for f in files:
        current_app.logger.debug("create_checksum: Adding " + f)
        filepath = os.path.join(upload_dir, f)
        with open(filepath, 'rb', buffering=0) as fp:
            while True:
                block = fp.read(buffersize)
                if not block:
                    break
                sha.update(block)
    cs = sha.hexdigest()
    record_add_field(rec, '024', ind1='7',
                         subfields = [('2', 'checksum'), ('a', cs)])
    return cs


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

