from invenio.sqlalchemyutils import db
from invenio.simplestore_model.metadata.linguistics_lang_codes import lang_codes
import json

domain = "Linguistics"
table_name = 'linguistics'
icon = 'icon-quote-right'

fields = [{'name':'language_code',
           'display_text':'Language Code',
           'col_type':db.String(128),
           'required':True,
           'description': 'Three letter ISO 639-3 code',
           'data_provide': 'typeahead',
           'data_source': json.dumps(lang_codes)},
          {'name':'region',
           'display_text':'Country/Region',
           'col_type':db.String(256)},
          {'name':'ling_resource_type',
           'display_text':'Linguistic Resource Type',
           'col_type':db.String(256),
           'required':True,
           'description': 'This element allows the depositor to specify the type ' +\
                          'of the resource (Text, Audio, Video, Time-Series, Photo, etc.)'},
          {'name':'project_name',
           'display_text':'Project Name',
           'col_type':db.String(256)},
          {'name':'quality',
           'display_text':'Quality',
           'col_type':db.String(256)}]
