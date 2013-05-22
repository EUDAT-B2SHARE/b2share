# -*- coding: utf-8 -*-

"""
SimpleStore File Upload

Functions to handle plupload js calls from deposit page.
Based on WebDeposit code.
"""
import shutil
import os
from glob import iglob
from werkzeug.utils import secure_filename
from flask import jsonify
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

        if int(chunk) == int(chunks) - 1:
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


#don't think we need this
def get_file(sub_id):
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


def check_status(sub_id):
    # setting to status to 1 causes a reload. I'm not sure when we want to do
    # this. Possibly when upload complete?
    return jsonify({"status": 0})


def check_status_noarg():
    # setting to status to 1 causes a reload. I'm not sure when we want to do
    # this. Possibly when upload complete?
    return jsonify({"status": 0})
