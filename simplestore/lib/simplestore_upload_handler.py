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
from uuid import uuid1 as new_uuid
from glob import iglob
import pickle

from werkzeug.utils import secure_filename

from flask import send_file, current_app

from invenio.config import CFG_SIMPLESTORE_UPLOAD_FOLDER


def upload(request, sub_id):
    """ The file is split into chunks on the client-side
        and reformed on the server-side.

        @sub_id - submission id
    """
    if request.method == 'POST':
        if sub_id.startswith('/'):
            # malformed uuid, can lead to data escalation, raise an error
            raise Exception('UUID is malformed')

        try:
            chunks = request.form['chunks']
            chunk = request.form['chunk']
        except KeyError:
            chunks = None
            chunk = 0

        # generate a unique name to be used for submission
        name = request.form['name']
        current_chunk = request.files['file']

        if not os.path.exists(CFG_SIMPLESTORE_UPLOAD_FOLDER):
            os.makedirs(CFG_SIMPLESTORE_UPLOAD_FOLDER)

        # webdeposit also adds userid and deptype folders, we just use unique id
        upload_dir = os.path.join(CFG_SIMPLESTORE_UPLOAD_FOLDER, sub_id)

        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)

        import hashlib
        hasher = hashlib.md5()
        hasher.update(name)
        md5 = hasher.hexdigest()

        # Save the chunk
        safename = secure_filename(name)
        filename = safename + "_" + md5 + "_" + chunk
        path_to_save = os.path.join(upload_dir, filename)
        current_chunk.save(path_to_save)
        current_app.logger.warning("    chunk %s" % (filename,))

        if (chunks is None) or (int(chunk) == int(chunks) - 1):
            '''All chunks have been uploaded! Start merging the chunks!'''
            merge_chunks_and_create_metadata(upload_dir, name, md5, safename)
    return filename

def merge_chunks_and_create_metadata(upload_dir, name, md5, safename):
    root, ext = os.path.splitext(safename)
    if ext in ['.gz', '.bz2']:
        ext = os.path.splitext(root)[1] + ext

    file_uuid_name = str(new_uuid()) + ext
    file_path = os.path.join(upload_dir, file_uuid_name)

    chunk_files = []
    for chunk_file in iglob(os.path.join(upload_dir, safename + "_" + md5 + '_*')):
        chunk_files.append(chunk_file)
    # Sort files in numerical order
    chunk_files.sort(key=lambda x: int(x.split("_")[-1]))

    with open(file_path, 'wb') as destination:
        for chunk in chunk_files:
            with open(chunk, 'rb') as chunk_fd:
                shutil.copyfileobj(chunk_fd, destination)
            os.remove(chunk)

    size = os.path.getsize(file_path)
    file_metadata = dict(name=name, file=file_path, size=size)

    # create a metadata_<uuid> file to store pickled metadata
    metadata_file_path = os.path.join(upload_dir, 'metadata_' + file_uuid_name)
    pickle.dump(file_metadata, open(metadata_file_path, 'wb'))
    current_app.logger.warning("just uploaded: %s, size %d, in %s" % (name, size, file_path))

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
    if not os.path.samefile(
                            CFG_SIMPLESTORE_UPLOAD_FOLDER,
                            os.path.commonprefix([CFG_SIMPLESTORE_UPLOAD_FOLDER,
                              os.path.realpath(filename)])):
        return "File " + filename + " not found", 404

    f = os.path.join(CFG_SIMPLESTORE_UPLOAD_FOLDER, sub_id, filename)
    if (os.path.isfile(f)):
        return send_file(f, attachment_filename=filename, as_attachment=True)
    else:
        return "File " + filename + " not found", 404
