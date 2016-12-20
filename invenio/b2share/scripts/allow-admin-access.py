"""
Loop over all the records in Invenio. Checks and if necessary updates
the firerole definition of private files.
"""

from __future__ import print_function

import sys

from invenio.base.factory import with_app_context

MAX_RECORD = 500

admin_email = None
do_the_update = False

@with_app_context()
def main():
    from invenio.legacy.search_engine import get_record
    from invenio.legacy.bibupload.engine import bibupload
    from invenio.legacy.bibrecord import create_record
    from invenio.legacy.bibdocfile.api import BibRecDocs

    if len(sys.argv) > 1 and sys.argv[1] == '--do-the-update':
        global do_the_update
        do_the_update = True

    if not admin_email:
        print ("Please set the internal admin_email value correctly")
        return
    else:
        print ("Using admin email: {}".format(admin_email))

    if do_the_update:
        print ("!!! Validating and updating fireroles")

    # Loop through list of records
    for recid in range(1, MAX_RECORD):
        recid = int(recid)
        record = get_record(recid)
        if not record:
            continue
        rec = BibRecDocs(recid, human_readable=True)
        if not rec:
            continue

        print ('Processing record: {0}'.format(recid))
        # print ('record: {0}'.format(record))

        try:
            open_access = record.get('542')[0][0][0][1]
            uploaded_by = record.get('856')[0][0][0][1]
        except TypeError as e:
            print('    ERROR while accessing fields:')
            print(e)
            continue
        print ('    Access: {}; Uploaded by: "{}"'.format(open_access, uploaded_by))
        if open_access == 'open':
            continue

        docs = rec.list_bibdocs()
        for d in docs:
            change_status_for_private_doc(d, uploaded_by)


def change_status_for_private_doc(doc, uploaded_by):
    """ Allows admin to access private files"""
    df = doc.list_latest_files()
    if df and df[0]:
        filename = df[0].get_full_name().decode('utf-8')
    else:
        print ("ERROR: cannot find filename of bibdoc")
        return

    status = doc.get_status().strip()
    if not status.startswith('firerole:'):
        return

    old = status[len('firerole:'):].split('\n')
    old = [x for x in old if x]
    print ("    status: {}".format(old))

    if len(old) == 3 \
            and 'allow email' in old[0] \
            and 'deny until' in old[1] \
            and 'allow any' in old[2]:
        new = [
            old[0],
            'allow email "{}"'.format(admin_email),
            old[1],
            old[2],
        ]
        new_status = 'firerole:' + '\n'.join(new)
        if do_the_update:
            doc.set_status(new_status)
            print ("    + Fixed firerole for file {}".format(filename.encode('utf-8')))
        print ("    new status: {}".format(new_status))
    elif len(old) == 2 \
            and 'allow email' in old[0] \
            and 'deny all' in old[1]:
        new = [
            old[0],
            'allow email "{}"'.format(admin_email),
            old[1],
        ]
        new_status = 'firerole:' + '\n'.join(new)
        if do_the_update:
            doc.set_status(new_status)
            print ("    + Fixed firerole for file {}".format(filename.encode('utf-8')))
        print ("    new status: {}".format(new_status))
    else:
        print ("    ! Unknown firerole for file {}:".format(filename.encode('utf-8')))


if __name__ == '__main__':
    main()
