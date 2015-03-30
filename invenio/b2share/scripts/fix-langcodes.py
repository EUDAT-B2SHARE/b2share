"""
Loop over a list of records in Invenio and fix language codes
"""

from pprint import pprint
from invenio.base.factory import with_app_context
from time import sleep

RECORDS = [1, 2, 3, 4, 5, 10, 13, 14, 26, 30, 31, 37]

VALUES = {
    1: 'ces',
    2: 'gsg',
    3: 'gsg',
    4: 'nld',
    5: 'nld',
    10: 'ces',
    13: 'ces',
    14: 'zxx',
    26: 'nld',
    30: 'dum',
    31: 'eng',
    37: 'ces',
}


@with_app_context()
def main():
    from invenio.legacy.search_engine import get_record
    from invenio.legacy.bibupload.engine import (
        bibupload,
    )
    from invenio.legacy.bibrecord import (
        record_add_field,
        record_delete_field,
    )

    # Loop through list of records
    for r in RECORDS:
        old_rec = get_record(r)
        rec = get_record(r)

        if not rec:
            break

        print('Processing record: {0}'.format(r))
        # pprint(rec)

        old_690 = [f[0] for f in rec.get('690', [])]
        new_690 = []
        for f in old_690:
            a = f[0]
            b = f[1]
            t = [a, (b[0], VALUES.get(r))] if (a[0] == 'a' and
                                               a[1] == 'language_code' and
                                               b[0] == 'b' and
                                               VALUES.get(r)) \
                else f
            new_690.append(t)

        if not new_690 == old_690:
            record_delete_field(rec, '690')
            for f in new_690:
                record_add_field(rec, '690', subfields=f)

            # pprint(rec)
            print('\nOld 690:')
            pprint(old_rec.get('690'))
            print('\nNew 690:')
            pprint(rec.get('690'))

            if raw_input('Bibupload (y/n)? ') == 'y':
                bibupload(rec, 'delete')
                sleep(5)
                bibupload(rec, 'replace')


if __name__ == '__main__':
    print("Starting!")
    main()
    print("Done!")
