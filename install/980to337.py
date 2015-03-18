"""
Loop over all records in Invenio and move 'resource type' metadata from '980' to '337'
"""

import itertools

from invenio.base.factory import with_app_context


@with_app_context()
def main():
    import invenio.modules.editor.models
    import invenio.modules.editor.views

    from invenio.legacy.search_engine import get_record
    from invenio.legacy.bibrecord import (
        record_delete_field,
        record_add_field,
    )
    from invenio.legacy.bibupload.engine import (
        bibupload,
    )

    for a in itertools.count(1):
        old_rec = get_record(a)
        rec = get_record(a)

        if not rec:
            break

        print('Processing record: {0}'.format(a))

        new_980 = []
        new_337 = []
        for f in rec.get('980', []):
            for sf in f[0]:
                if sf[0] == 'a' and sf[1] in ['Text', 'Image', 'Video', 'Audio', 'Time-Series', 'Other']:
                    new_337.append(sf)
                else:
                    new_980.append(sf)

        if new_337:
            record_delete_field(rec, '980')
            record_add_field(rec, '337', subfields=new_337)
            record_add_field(rec, '980', subfields=new_980)

            print('Old 337: {0}'.format(old_rec.get('337')))
            print('New 337: {0}'.format(rec.get('337')))
            print('Old 980: {0}'.format(old_rec.get('980')))
            print('New 980: {0}'.format(rec.get('980')))
            if raw_input('Bibupload (y/n)? ') == 'y':
                bibupload(rec, 'replace')


if __name__ == '__main__':
    print("Starting!")
    main()
    print("Done!")
