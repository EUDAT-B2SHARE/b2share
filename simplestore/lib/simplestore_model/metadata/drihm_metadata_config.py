from invenio.sqlalchemyutils import db


domain = "drihm"
display_name = "DRIHM"
table_name = 'drihm'
image = 'drihm_icon.jpg'
kind = 'project'

# note that fields will need more stuff like validators later
fields = [{'name':'hydrology',
           'col_type':db.String(256),
           'required':True},
          {'name':'hydraulic',
           'col_type':db.String(256)},
          {'name':'meteorology',
           'col_type':db.String(256)},
          {'name':'flooding',
           'col_type':db.String(256)},
          {'name':'storm',
           'col_type':db.String(256)},
          {'name':'citizenscientist',
           'display_text':'Citizen Scientist',
           'col_type':db.String(256)},
          {'name':'observation',
           'col_type':db.String(256)},
          {'name':'research',
           'col_type':db.String(256)},
          {'name':'data',
           'col_type':db.String(256)},
          {'name':'model',
           'col_type':db.String(256)},
          {'name':'rainfall',
           'col_type':db.Numeric()},
          {'name':'discharge',
           'col_type':db.String(256)},
          {'name':'hydrograph',
           'col_type':db.String(256)},
          {'name':'rainguage',
           'display_text':'Rain Guage',
           'col_type':db.String(256)},
          {'name':'weather',
           'col_type':db.String(256)},
          {'name':'experiment',
           'col_type':db.String(256)}]
