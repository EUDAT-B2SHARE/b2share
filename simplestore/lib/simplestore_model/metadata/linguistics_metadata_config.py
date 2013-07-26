from invenio.sqlalchemyutils import db


domain = "Linguistics"
table_name = 'linguistics'
icon = 'icon-quote-right'
# note that fields will need more stuff like validators later
fields = [{'name':'language_code',
           'display_text':'Language Code',
           'col_type':db.String(3),
           'required':True},
          {'name':'region',
           'display_text':'Country/Region',
           'col_type':db.String(256)},
          {'name':'ling_resource_type',
           'display_text':'Linguistic Resource Type',
           'col_type':db.String(256),
           'required':True},
          {'name':'project_name',
           'display_text':'Project Name',
           'col_type':db.String(256)},
          {'name':'quality',
           'display_text':'Quality',
           'col_type':db.String(256)}]
