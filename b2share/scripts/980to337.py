"""
Loop over all records in Invenio and move 'resource type' metadata from '980' and 'ling_resource_type' from '690' to '337'
"""

from pprint import pprint
import itertools

from invenio_base.factory import with_app_context

TYPES = ['Text', 'Image', 'Video', 'Audio', 'Time-Series', 'Other']


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

        old_337 = [f[0] for f in rec.get('337', [])]
        new_337 = old_337[:]
        new_690 = []
        new_980 = []
        for f in rec.get('980', []):
            for sf in f[0]:
                if sf[0] == 'a' and sf[1] in TYPES:
                    if [sf] not in new_337:
                        new_337.append([sf])
                else:
                    if [sf] not in new_980:
                        new_980.append([sf])

        for f in rec.get('690', []):
            sfs = f[0]
            if sfs[0][0] == 'a' and sfs[0][1] == 'ling_resource_type':
                res_type = sfs[1][1]
                if res_type in TYPES:
                    if [('a', res_type)] not in new_337:
                        new_337.append([('a', res_type)])
                else:
                    print("Unrecognized 'ling_resource_type' value! '{0}'".format(res_type))
            else:
                if sfs not in new_690:
                    new_690.append(sfs)

        if not new_337 == old_337:
            record_delete_field(rec, '337')
            record_delete_field(rec, '980')
            record_delete_field(rec, '690')
            for f in new_337:
                record_add_field(rec, '337', subfields=f)
            for f in new_980:
                record_add_field(rec, '980', subfields=f)
            for f in new_690:
                record_add_field(rec, '690', subfields=f)

            print('\nOld 337:')
            pprint(old_rec.get('337'))
            print('New 337:')
            pprint(rec.get('337'))

            print('\nOld 690:')
            pprint(old_rec.get('690'))
            print('New 690:')
            pprint(rec.get('690'))

            print('\nOld 980:')
            pprint(old_rec.get('980'))
            print('New 980:')
            pprint(rec.get('980'))
            if raw_input('Bibupload (y/n)? ') == 'y':
                bibupload(rec, 'replace')


if __name__ == '__main__':
    print("Starting!")
    main()
    print("Done!")
