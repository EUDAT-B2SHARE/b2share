# -*- coding: utf-8 -*-

"""
SimpleStore File Upload

Uses plupload. Based on WebDeposit code.
"""
import shutil
import os
import uuid
from glob import iglob
from werkzeug.utils import secure_filename
from flask import jsonify

CFG_SIMPLESTORE_UPLOAD_FOLDER = '/opt/invenio/var/tmp/simplestore_uploads'


def upload(request, uid):
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


def delete(request, id):
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
def get_file(uuid):
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


def check_status(uuid):
    # setting to status to 1 causes a reload. I'm not sure when we want to do
    # this. Possibly when upload complete?
    return jsonify({"status": 0})


def check_status_noarg():
    # setting to status to 1 causes a reload. I'm not sure when we want to do
    # this. Possibly when upload complete?
    return jsonify({"status": 0})
