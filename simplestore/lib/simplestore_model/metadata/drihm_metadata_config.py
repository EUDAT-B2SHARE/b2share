from invenio.sqlalchemyutils import db

from datetime import date


domain = "drihm"
display_name = "Hydro-Meteorology"
table_name = 'DRIHM'
image = 'domain-drihm.png'
kind = 'project'
description = 'This domain is for meteorology or climate data.'

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
          {'name': 'topic',
           'col_type': db.String(256),
           'display_text': 'Topic Category',
           'required': True},
           {'name': 'responsible_party',
           'col_type': db.String(256),
           'display_text': 'Responsible Party',
           'required': True},
           {'name': 'geo_location',
           'col_type': db.String(256),
           'display_text': 'Geographic Location',
           'required': True},
           {'name': 'spatial_resolution',
           'col_type': db.String(256),
           'display_text': 'Spatial Resolution',
           'required': True},
           {'name': 'vertical_extent',
           'col_type': db.String(256),
           'display_text': 'Vertical Extent',
           'required': True},
          {'name': 'lineage',
           'col_type': db.String(256),
           'display_text': 'Lineage',
           'required': True}
         ]

