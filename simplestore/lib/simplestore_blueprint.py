# -*- coding: utf-8 -*-
# #
# # This file is part of Invenio.
# # Copyright (C) 2012, 2013 CERN.
# #
# # Invenio is free software; you can redistribute it and/or
# # modify it under the terms of the GNU General Public License as
# # published by the Free Software Foundation; either version 2 of the
# # License, or (at your option) any later version.
# #
# # Invenio is distributed in the hope that it will be useful, but
# # WITHOUT ANY WARRANTY; without even the implied warranty of
# # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# # General Public License for more details.
# #
# # You should have received a copy of the GNU General Public License
# # along with Invenio; if not, write to the Free Software Foundation, Inc.,
# # 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""SimpleStore Flask Blueprint"""
import os
import uuid
import urllib2
import shutil
import time
from glob import iglob
from flask import (render_template, request, jsonify, url_for,
                   send_from_directory, flash)
from werkzeug.utils import secure_filename
from flask.ext.wtf import Form, TextField
from flask.ext.wtf.html5 import EmailField
from invenio.webinterface_handler_flask_utils import _, InvenioBlueprint
from invenio.config import CFG_SITE_SECRET_KEY
from invenio.sqlalchemyutils import db
from invenio.simplestore_model.model import Submission, SubmissionMetadata, LinguisticsMetadata
from invenio.bibtask import task_low_level_submission
from wtforms.ext.sqlalchemy.orm import model_form
from invenio.simplestore_model.HTML5ModelConverter import HTML5ModelConverter
from invenio.bibfield_jsonreader import JsonReader
from tempfile import mkstemp
from invenio.config import CFG_TMPSHAREDDIR

blueprint = InvenioBlueprint('simplestore', __name__,
                             url_prefix='/simplestore',
                             menubuilder=[('main.simplestore',
                                          _('SimpleStore'),
                                          'simplestore.deposit', 2)],
                             breadcrumbs=[(_('SimpleStore'),
                                          'simplestore.deposit')])

CFG_SIMPLESTORE_UPLOAD_FOLDER = '/opt/invenio/var/tmp/simplestore_uploads'


@blueprint.route('/')
def deposit():
    """ Renders the deposit """
    #this is going to break on reload, does it matter?
    return render_template('simplestore-deposit.html', uuid=uuid.uuid1().hex)


class OtherForm(Form):
    SECRET_KEY = CFG_SITE_SECRET_KEY
    author = TextField('Author')
    title = TextField('Title')
    keywords = TextField('Keywords')
    pub = TextField('Publication')
    email = EmailField('Email')

    #using generator allows us to order output and avoid csrf field
    def basic_field_iter(self):
        for f in [self.author, self.title, self.keywords]:
            yield f

    def adv_field_iter(self):
        yield self.pub
        yield self.email


class FormWithKey(Form):
    SECRET_KEY = CFG_SITE_SECRET_KEY


@blueprint.route('/upload/<uid>', methods=['POST'])
def plupload(uid):
    """ The file is split into chunks on the client-side
        and reformed on the server-side
    """
    if request.method == 'POST':
        try:
            chunks = request.form['chunks']
            chunk = request.form['chunk']
        except KeyError:
            chunks = None
            pass
        name = request.form['name']
        current_chunk = request.files['file']

        try:
            filename = secure_filename(name) + "_" + chunk
        except UnboundLocalError:
            filename = secure_filename(name)

        if not os.path.exists(CFG_SIMPLESTORE_UPLOAD_FOLDER):
            os.makedirs(CFG_SIMPLESTORE_UPLOAD_FOLDER)

        # webdeposit also adds userid and deptype folders
        CFG_USER_SIMPLESTORE_FOLDER = os.path.join(
            CFG_SIMPLESTORE_UPLOAD_FOLDER, uid)

        if not os.path.exists(CFG_USER_SIMPLESTORE_FOLDER):
            os.makedirs(CFG_USER_SIMPLESTORE_FOLDER)

        # Save the chunk
        current_chunk.save(os.path.join(CFG_USER_SIMPLESTORE_FOLDER, filename))

        unique_filename = ""

        if chunks is None:  # file is a single chunk
            unique_filename = str(uuid.uuid1()) + filename
            old_path = os.path.join(CFG_USER_SIMPLESTORE_FOLDER, filename)
            file_path = os.path.join(CFG_USER_SIMPLESTORE_FOLDER,
                                     unique_filename)
            os.rename(old_path, file_path)  # Rename the chunk
            #size = os.path.getsize(file_path)
            #file_metadata = dict(name=name, file=file_path, size=size)
            #draft_field_list_add(current_user.get_id(), uuid,
            #                     "files", file_metadata)
        elif int(chunk) == int(chunks) - 1:
            '''All chunks have been uploaded!
                start merging the chunks'''
            filename = secure_filename(name)
            chunk_files = []
            for chunk_file in iglob(os.path.join(CFG_USER_SIMPLESTORE_FOLDER,
                                                 filename + '_*')):
                chunk_files.append(chunk_file)

            # Sort files in numerical order
            chunk_files.sort(key=lambda x: int(x.split("_")[-1]))

            unique_filename = str(uuid.uuid1()) + filename
            file_path = os.path.join(CFG_USER_SIMPLESTORE_FOLDER,
                                     unique_filename)
            destination = open(file_path, 'wb')
            for chunk in chunk_files:
                shutil.copyfileobj(open(chunk, 'rb'), destination)
                os.remove(chunk)
            destination.close()
            #size = os.path.getsize(file_path)
            #file_metadata = dict(name=name, file=file_path, size=size)
            #draft_field_list_add(current_user.get_id(), uuid,
            #                     "files", file_metadata)
    return unique_filename


@blueprint.route('/plupload_delete/<id>', methods=['GET', 'POST'])
def plupload_delete(id):
    if request.method == 'POST':
        #filename = request.form['filename']
        files = os.listdir(os.path.join(CFG_SIMPLESTORE_UPLOAD_FOLDER, id))
        # delete all for minute
        for f in files:
            os.remove(f)
            result = "File " + f['name'] + " Deleted"
            break
    return result


#don't think we need this
@blueprint.route('/plupload_get_file/<uuid>', methods=['GET'])
def plupload_get_file(uuid):
#    filename = request.args.get('filename')
#    tmp = ""
#    files = draft_field_get(current_user.get_id(), uuid, "files")
#    for f in files:
#        tmp += f['file'].split('/')[-1] + '<br><br>'
#        if filename == f['file'].split('/')[-1]:
#            return send_file(f['file'],
#                             attachment_filename=f['name'],
#                             as_attachment=True)
#
#    return "filename: " + filename + '<br>' + tmp
    return ""


@blueprint.route('/check_status/<uuid>/', methods=['GET', 'POST'])
def check_status(uuid):
    # setting to status to 1 causes a reload. I'm not sure when we want to do
    # this. Possibly when upload complete?
    return jsonify({"status": 0})


@blueprint.route('/check_status/', methods=['GET', 'POST'])
def check_status_noarg():
    # setting to status to 1 causes a reload. I'm not sure when we want to do
    # this. Possibly when upload complete?
    return jsonify({"status": 0})


@blueprint.route('/addmeta', methods=['POST'])
def addmeta():
    #Uncomment the following line if there are errors regarding db tables
    #not being present. Hacky solution for minute.

    #db.create_all()

    sub = ""
    if 'uuid' in request.form:
        sub = Submission.query.filter_by(uuid=request.form['uuid']).first()
        if sub is None:
            sub = Submission(uuid=request.form['uuid'])

            if request.form['domain'] == 'linguistics':
                meta = LinguisticsMetadata()
            else:
                meta = SubmissionMetadata()

            sub.md = meta
            db.session.add(sub)
            db.session.commit()
    else:
        return "ERROR: uuid not set", 500

    MetaForm = model_form(sub.md.__class__, base_class=FormWithKey,
                          exclude=['submission', 'submission_type'],
                          converter=HTML5ModelConverter())
    meta_form = MetaForm(request.form, sub.md)

    if meta_form.validate_on_submit():
        create_marc_and_ingest(request.form)
        return render_template('simplestore-finalise.html', tag=sub.uuid)
    #else:
    #   print meta_form.errors

    files = os.listdir(os.path.join(CFG_SIMPLESTORE_UPLOAD_FOLDER, request.form['uuid']))

    return render_template(
        'simplestore-addmeta.html',
        domain=request.form['domain'],
        fileret=files,
        form=meta_form,
        uuid=sub.uuid,
        basic_field_iter=sub.md.basicFieldIter,
        opt_field_iter=sub.md.optionalFieldIter,
        getattr=getattr)


def create_marc_and_ingest(form):
    json_reader = JsonReader()
    # just do this by hand to get something working for demo
    # this must be automated
    json_reader['title.title'] = form['title']
    json_reader['authors[0].full_name'] = form['creator']
    json_reader['imprint.publisher_name'] = form['publisher']
    json_reader['collection.primary'] = "Article"
    marc = json_reader.legacy_export_as_marc()
    tmp_file_fd, tmp_file_name = mkstemp(suffix='.marcxml',
                                         prefix="webdeposit_%s" % time.strftime("%Y-%m-%d_%H:%M:%S"),
                                         dir=CFG_TMPSHAREDDIR)
    os.write(tmp_file_fd, marc)
    os.close(tmp_file_fd)
    os.chmod(tmp_file_name, 0644)
    task_low_level_submission('bibupload', 'webdeposit', '-i', tmp_file_name)


@blueprint.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'GET':

        #Possibly not correct, but trying to mimic requests on working code
        return ""

    if request.method == 'POST':

        #You can't use the data_file.content_length method as it is 0 usually
        #Note that I've hard coded the server name, obviously you will need
        #to fix this

        data_file = request.files['files[]']
        dir_id = str(uuid.uuid4())
        temp_dir_name = str(blueprint.config['UPLOAD_FOLDER']) + "/" + dir_id
        try:
            os.makedirs(temp_dir_name)
        except OSError as ex:
            flash("Caught Server Error: " + ex.strerror)

        sec_file = secure_filename(data_file.filename)
        file_name = os.path.join(temp_dir_name, sec_file)
        data_file.save(file_name)

        #Can also supply a thumbnail url, but I don't think we need to

        return jsonify(
            files=[dict(
                name=sec_file,
                size=os.stat(file_name).st_size,  # content_length usually 0
                type=data_file.content_type,
                delete_url=url_for('getfiles', dir_id=dir_id,
                                   filename=sec_file),
                delete_type="DELETE",
                url=url_for('getfiles', dir_id=dir_id, filename=sec_file))])


#Handle getting and deleting of files
@blueprint.route('/files/<dir_id>/<filename>', methods=['GET', 'DELETE'])
def getfiles(dir_id, filename):
    if request.method == 'GET':

        return send_from_directory(blueprint.config['UPLOAD_FOLDER'] + "/" + dir_id,
                                   urllib2.unquote(filename))

    if request.method == 'DELETE':

        file_dir = blueprint.config['UPLOAD_FOLDER'] + "/" + dir_id
        try:
            os.remove(file_dir + "/" + urllib2.unquote(filename))
            if not os.listdir(file_dir):
                os.rmdir(file_dir)
        except OSError as ex:
            flash("Caught Server Error: " + ex.strerror)

        return ""


@blueprint.route('/finalise', methods=['POST'])
def finalise():
    return render_template('simplestore-finalise.html', tag=uuid.uuid4())
