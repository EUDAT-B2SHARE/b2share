# -*- coding: utf-8 -*-

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

"""
SimpleStore File Upload

Functions to handle plupload js calls from deposit page.
Based on WebDeposit code.
"""
import shutil
import os
from glob import iglob
from werkzeug.utils import secure_filename
from flask import send_file
from invenio.config import CFG_SIMPLESTORE_UPLOAD_FOLDER


def upload(request, sub_id):
    """ The file is split into chunks on the client-side
        and reformed on the server-side.

        WebDeposit used unique filenames - don't think this is needed if we
        have unique directories.
    """
    if request.method == 'POST':
        try:
            chunks = request.form['chunks']
            chunk = request.form['chunk']
        except KeyError:
            chunks = None
            pass
        # generate a unique name to be used for submission
        name = request.form['name']
        current_chunk = request.files['file']

        try:
            filename = secure_filename(name) + "_" + chunk
        except UnboundLocalError:
            filename = secure_filename(name)

        if not os.path.exists(CFG_SIMPLESTORE_UPLOAD_FOLDER):
            os.makedirs(CFG_SIMPLESTORE_UPLOAD_FOLDER)

        # webdeposit also adds userid and deptype folders, we just use unique
        # id
        upload_dir = os.path.join(CFG_SIMPLESTORE_UPLOAD_FOLDER, sub_id)

        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)

        # Save the chunk
        current_chunk.save(os.path.join(upload_dir, filename))

        if (chunks is not None) and (int(chunk) == int(chunks) - 1):
            '''All chunks have been uploaded!
                start merging the chunks'''
            filename = secure_filename(name)
            chunk_files = []
            for chunk_file in iglob(os.path.join(upload_dir,
                                                 filename + '_*')):
                chunk_files.append(chunk_file)

            # Sort files in numerical order
            chunk_files.sort(key=lambda x: int(x.split("_")[-1]))

            file_path = os.path.join(upload_dir, filename)
            destination = open(file_path, 'wb')
            for chunk in chunk_files:
                shutil.copyfileobj(open(chunk, 'rb'), destination)
                os.remove(chunk)
            destination.close()

    return filename


def delete(request, sub_id):
    """
    Deletes file with name form['filename'] if it exists in upload_dir.

    Could change to return error if nothing deleted.
    Also should we be using secure_filename ?
    """

    result = ""

    upload_dir = os.path.join(CFG_SIMPLESTORE_UPLOAD_FOLDER, sub_id)
    filename = request.form['filename']

    files = os.listdir(upload_dir)
    # delete all for minute
    for f in files:
        if f == filename:
            os.remove(os.path.join(upload_dir, f))
            result = "File " + f + " Deleted"
            break
    if result == "":
        return "File " + filename + "not found", 404

    return result


def get_file(request, sub_id):
    """
    Returns uploaded file.

    I don't really think we need this, but it's easier to implement than to
    remove the functionality.
    """
    filename = request.args.get('filename')
    # make sure that request doesn't go outside the CFG_SIMPLESTORE_UPLOAD_FOLDER
    if os.path.isabs(filename):
        return 'File ' + filename + " not found", 404
    f = os.path.join(CFG_SIMPLESTORE_UPLOAD_FOLDER, sub_id, filename)
    if (os.path.isfile(f)):
        return send_file(f, attachment_filename=filename, as_attachment=True)
    else:
        return "File " + filename + " not found", 404
