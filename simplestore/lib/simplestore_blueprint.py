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

"""WebDeposit Flask Blueprint"""
import os
import shutil
import json
import uuid
import logging
import urllib2
from glob import iglob
from flask import Flask, \
                  current_app, \
                  render_template, \
                  request, \
                  jsonify, \
                  redirect, \
                  url_for, \
                  send_from_directory, \
                  flash
from werkzeug.utils import secure_filename
from invenio.sqlalchemyutils import db
from flask.ext.bootstrap import Bootstrap
from flask.ext.wtf import Form, TextField
from flask.ext.wtf.html5 import EmailField
from invenio.webinterface_handler_flask_utils import _, InvenioBlueprint

blueprint = InvenioBlueprint('ssdeposit', __name__,
                              url_prefix='/ssdeposit',
                              menubuilder=[('main.ssdeposit',
                                          _('SSDeposit'),
                                            'ssdeposit.index_deposition_types', 2)],
                              breadcrumbs=[(_('SSDeposit'), 'ssdeposit.index_deposition_types')])


@blueprint.route('/')
def index_deposition_types():
    """ Renders the deposit """
    return render_template('simplestore-home.html')

class OtherForm(Form):
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

@blueprint.route('/addmeta', methods=['POST'])
def addmeta():
    print 'here'
    form = OtherForm()

    return render_template('simplestore-addmeta.html',
        domain=request.form['domain'],
        fileret=request.form.get('filelist'),
        form=form)

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


@blueprint.route('/deposit')
def deposit():
    """ Renders the deposit """
    return render_template('simplestore-deposit.html')





