import os
from invenio.dbquery import run_sql
from invenio.bibrecord import record_add_field, record_xml_output
from invenio.config import CFG_SIMPLESTORE_UPLOAD_FOLDER


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


def create_recid():
    """
    Uses the DB to get a record id for the submission.
    """
    return run_sql("INSERT INTO bibrec(creation_date, modification_date) "
                   "values(NOW(), NOW())")


def add_file_info(rec, form, email, sub_id):
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
        record_add_field(rec, 'FFT',
                         subfields=[('a', os.path.join(upload_dir, f)),
                         #('d', 'some description') # TODO
                         #('t', 'Type'), # TODO
                         ('r', fft_status)])


def create_marc(form, sub_id, email):
    """
    Generates MARC data used by Invenio from the filled out form, then
    submits it to the Invenio system.
    """
    rec = {}
    recid = create_recid()
    record_add_field(rec, '001', controlfield_value=str(recid))

    add_basic_fields(rec, form, email)
    add_file_info(rec, form, email, sub_id)

    marc = record_xml_output(rec)

    return recid, marc
