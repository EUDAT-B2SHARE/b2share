from invenio.sqlalchemyutils import db

from datetime import date


domain = "euon"
display_name = "EUON"
table_name = 'euon'
image = 'euon_icon.jpg'
kind = 'project'


# note that fields will need more stuff like validators later
fields = [
          {'name': 'ref_date',
           'col_type': db.Date(),
           'display_text': 'Reference date',
           'required': True,
           'default': date.today()},
          {'name': 'reference_system',
           'col_type': db.String(256),
           'display_text': 'Reference System',
           'required': True},
         ]

