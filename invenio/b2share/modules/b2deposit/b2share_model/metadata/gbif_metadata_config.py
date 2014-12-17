from invenio.ext.sqlalchemy import db

domain = 'GBIF'
# display_name = 'Global Biodiversity Information Facility'
display_name = 'Biodiversity'
table_name = 'GBIF'
image = 'domain-gbif.png'
kind = 'project'
domaindesc = 'Biodiversity data.'

fields = [
    {
        'name': 'version_number',
        'col_type': db.Integer(),
        'display_text': 'Version number',
        'description': 'Version number',
        'required': True,
    },
    {
        'name': 'gbif_id',
        'col_type': db.String(256),
        'display_text': 'GBIF ID',
        'description': 'Refers to GBIF metadataset',
        'required': True,
    },
    {
        'name': 'country',
        'col_type': db.String(256),
        'display_text': 'Country',
        'description': 'Country',
        'required': True,
    },
    {
        'name': 'status',
        'col_type': db.String(256),
        'display_text': 'Status',
        'description': 'Endorsement status',
        'required': True,
    },
]
