"""
Loop over a list of records in Invenio and restore from revision archive
"""

from pprint import pprint
from invenio_base.factory import with_app_context
from time import sleep

# RECORDS = [1, 2, 3, 4, 5, 10, 13, 14, 26, 30, 31, 37]
RECORDS = [13]


@with_app_context()
def main():
    from invenio.legacy.search_engine import get_record
    from invenio.legacy.bibupload.engine import (
        bibupload,
    )
    from invenio.legacy.bibrecord import (
        create_record,
    )
    from invenio.legacy.bibedit.db_layer import get_record_revisions
    from invenio.legacy.bibedit.utils import (
        get_record_revision_ids,
        get_marcxml_of_revision,
    )

    # Loop through list of records
    for r in RECORDS:
        rec = get_record(r)

        if not rec:
            break

        print('Processing record: {0}'.format(r))
        # pprint(rec)

        print(get_record_revision_ids(r))
        print

        revs = get_record_revisions(r)
        print(revs)
        print

        for id, rev in revs[0:1]:
            marcxml = get_marcxml_of_revision(r, rev)
            # print(marcxml)
            # print
            rec = create_record(marcxml)[0]
            pprint(rec)

            if raw_input('Bibupload (y/n)? ') == 'y':
                # bibupload(rec, 'delete')
                # sleep(5)
                bibupload(rec, 'replace')


if __name__ == '__main__':
    print("Starting!")
    main()
    print("Done!")
