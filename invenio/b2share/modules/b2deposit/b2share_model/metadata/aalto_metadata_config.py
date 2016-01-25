from linguistics_lang_codes import lang_codes
from invenio.ext.sqlalchemy import db

domain = 'Aalto'
# display_name = 'Research Data Alliance'
display_name = 'Aalto'
table_name = 'Aalto'
image = 'domain-aalto.jpg'
kind = 'project'
domaindesc = 'Aalto University'

# the domain administators can edit even published records
admin_can_edit_published_record = True

# only the domain administrators can deposit
depositing_groups = ['aalto_domain_administrators','aalto_domain_members']

fields = [
    {
        'name': 'owner_org',
        'col_type': db.String(256),
        'display_text': 'Owner Organisation',
        'description': 'Owner Organisation',
        'required': True,
    },
    {
        'name': 'owner',
        'col_type': db.String(256),
        'display_text': 'Owner',
        'description': 'Owner',
        'required': False,
    },
    {
        'name': 'funder',
        'col_type': db.String(256),
        'display_text': 'Funder',
        'description': 'Funder',
        'required': False,
    },
    {
        'name': 'funding_id',
        'col_type': db.String(256),
        'display_text': 'Funding ID',
        'description': 'Funding ID',
        'required': False,
    },
    {
        'name': 'project_name',
        'col_type': db.String(256),
        'display_text': 'Project Name',
        'description': 'Project Name',
        'required': False,
    },
    {
        'name': 'project_url',
        'col_type': db.String(256),
        'display_text': 'Project URL',
        'description': 'Project URL',
        'required': False,
    },
    {
        'name': 'language_code',
        'display_text': 'Language Code',
        'col_type': db.String(128),
        'required': True,
        'value': 'eng',
        'description': 'This element can be used to add an ISO language code from '
                       'ISO-639-3 to uniquely identify the language a document '
                       'is written in',
        'data_provide': 'select',
        'data_source': [(c, u'{c} [{n}]'.format(c=c, n=n.decode('utf-8'))) for c, n in lang_codes]
    },
]
