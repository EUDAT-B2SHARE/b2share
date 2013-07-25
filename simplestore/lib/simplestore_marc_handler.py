import os
from itertools import chain
from datetime import datetime
from invenio.dbquery import run_sql
from invenio.bibrecord import record_add_field, record_xml_output
<<<<<<< HEAD
from invenio.config import CFG_SIMPLESTORE_UPLOAD_FOLDER
from invenio.config import CFG_SITE_SECURE_URL
from invenio.config import CFG_SITE_NAME
from invenio.config import (CFG_SIMPLESTORE_UPLOAD_FOLDER, CFG_SITE_NAME,
                            CFG_SITE_SECURE_URL)
from invenio.simplestore_model.model import SubmissionMetadata
from invenio.simplestore_epic import createHandle


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

    if form['keywords']:
        for kw in form['keywords'].split(','):
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
        fft_status = 'firerole: allow email "{0}"\nfirerole: deny all\n'.format(
            email)
    for f in files:
        path = os.path.join(upload_dir, f)
        record_add_field(rec, 'FFT',
                         subfields=[('a', path),
                         #('d', 'some description') # TODO
                         #('t', 'Type'), # TODO
                         ('r', fft_status)])

        # Because of the way invenio works, we need to add any further data
        # directly to the record and hope it merges properly later.
        url = "{0}/record/{1}/files/{2}".format(CFG_SITE_SECURE_URL, recid, f)
        record_add_field(rec, '856', ind1='4',
                         subfields=[('u', url),
                                    ('s', str(os.path.getsize(path)))])


def add_domain_fields(rec, form):
    """
    Adds a domain specific fields. These are just added as name value pairs
    to field 690.
    """

    # At the moment we just assume any field *not* from SubmissionMetadata is
    # an extra field. There's probably a better way to do this.

    special_fields = ['files', 'domain', 'sub_id', 'csrf_token', 'action_save']
    sm = SubmissionMetadata()
    ignore_fields = chain(sm.basic_field_iter(),
                          sm.optional_field_iter(),
                          special_fields)

    for k in (set(form.keys()) - set(ignore_fields)):
        if form[k]:
            record_add_field(rec, '690', subfields=[('a', k), ('b', form[k])])


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

    #TODO - replace by a call to get a genuine EPIC PID
    location = CFG_SITE_SECURE_URL + '/record/' + str(recid)
    pid = createHandle(location)
    #pid = '12.3456/dummy.pid.78910'
    record_add_field(rec, '024', ind1='7', subfields = [('2', 'PID'), ('a', pid)])

    marc = record_xml_output(rec)

    return recid, marc
