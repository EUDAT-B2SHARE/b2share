from invenio.ext.sqlalchemy import db

domain = "LTER"
display_name = "LTER"
table_name = 'lter'
image = 'domain-lter.jpg'
kind = 'project'
domaindesc = 'LTER Europe'

fields = [
    {
        'name': 'metadata_url',
        'col_type': db.String(256),
        'display_text': 'Metadata URL',
        'description': 'The location of the full metadata record',
    },
]
