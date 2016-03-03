"""
Loop over all the records in Invenio. Checks and if necessary updates
the firerole definition of private files.
"""

from __future__ import print_function

import sys

from invenio.base.factory import with_app_context

#RECORDS = [256,258,263,266,267,269,279,282,283,286,295,306,311,316,326]

MAX_RECORD = 500

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

    if do_the_update:
        print ("!!! Validating and updating fireroles")

    # Loop through list of records
    for recid in range(1, MAX_RECORD):
        recid = int(recid)
        record = get_record(recid)
        if not record or not record.get('245'):
            continue
        rec = BibRecDocs(recid, human_readable=True)
        if not rec:
            continue

        print ('Processing record: {0}'.format(recid))
        # print ('record: {0}'.format(record))

        open_access = record.get('542')[0][0][0][1]
        uploaded_by = record.get('856')[0][0][0][1]
        print ('    Access: {}; Uploaded by: "{}"'.format(open_access, uploaded_by))
        if open_access == 'open':
            continue

        docs = rec.list_bibdocs()
        for d in docs:
            validate_status_for_private_doc(d, uploaded_by)


def validate_status_for_private_doc(doc, uploaded_by):
    """ Checks the access definition for this file. If it doesn't match the
        open_access value, the access is rewritten to only allow owner"""
    df = doc.list_latest_files()
    if df and df[0]:
        filename = df[0].get_full_name().decode('utf-8')
    else:
        print ("ERROR: cannot find filename of bibdoc")
        return

    status = doc.get_status().strip()
    if not status.startswith('firerole:'):
        return

    status = status[len('firerole:'):].split('\n')
    status = [x for x in status if x]
    print ("    status: {}".format(status))

    if len(status) == 2 \
            and 'deny until' in status[0] \
            and 'allow any' in status[1]:
        print ("    ! Bad firerole for file {}".format(filename))
        new_status = 'firerole:' + '\n'.join([
            'allow email "{0}"'.format(uploaded_by),
            status[0], # deny until
            'deny all'
        ])
        if do_the_update:
            doc.set_status(new_status)
            print ("    + Fixed firerole for file {}".format(filename))


if __name__ == '__main__':
    main()
