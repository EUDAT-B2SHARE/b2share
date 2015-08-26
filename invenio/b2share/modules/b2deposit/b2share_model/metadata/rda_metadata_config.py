from invenio.ext.sqlalchemy import db
from datetime import date

domain = 'RDA'
# display_name = 'Research Data Alliance'
display_name = 'RDA'
table_name = 'RDA'
image = 'domain-rda.png'
kind = 'project'
domaindesc = 'Research Data Alliance.'

# the domain administators can edit even published records
admin_can_edit_published_record = True

# only the domain administrators can deposit
depositing_groups = ['rda_domain_administrators']

fields = [
    {
        'name': 'date',
        'col_type': db.Date(),
        'display_text': 'Date',
        'description': 'Date',
        'required': False,
        'default': date.today()
    },
    {
        'name': 'coverage',
        'col_type': db.String(256),
        'display_text': 'Coverage',
        'description': 'Coverage',
        'required': False,
    },
    {
        'name': 'format',
        'col_type': db.String(256),
        'display_text': 'Format',
        'description': 'Format',
        'required': False,
    },
    {
        'name': 'relation',
        'col_type': db.String(256),
        'display_text': 'Relation',
        'description': 'Relation',
        'required': False,
    },
    {
        'name': 'source',
        'col_type': db.String(256),
        'display_text': 'Source',
        'description': 'Source',
        'required': False,
    },
]
