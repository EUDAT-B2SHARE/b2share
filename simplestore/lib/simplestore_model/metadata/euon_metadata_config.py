from invenio.sqlalchemyutils import db

from datetime import date


domain = "euon"
display_name = "EUON"
table_name = 'euon'
image = 'EUON-logo.png'
kind = 'project'


# note that fields will need more stuff like validators later
fields = [
          {'name': 'hasDomain',
           'col_type': db.String(256),
           'display_text': 'Ontology Domain',
           'required': True},
          {'name': 'hasOntologyLanguage',
           'col_type': db.String(256),
           'display_text': 'Ontology Language',
           'required': True},
          {'name': 'usedOntologyEngineeringTool',
           'col_type': db.String(256),
           'display_text': 'Ontology Engineering Tool ',
           'required': True},
         ]         