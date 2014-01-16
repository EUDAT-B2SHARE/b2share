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



# hasDomain	a category that describes the ontology, from a pre-defined list of categories (e.g., Anatomy, names of specific organisms, Diseases, etc.)	We have to create a list of domains: proposed take list of bioportal and widen it.
# hasOntologyLanguage	the language in which the ontology was developed	We have to setup a list of formal languages
# usedOntologyEngineeringTool	the tool that was used to develop the ontology	If someone wants to look on it
# creationDate, modificationDate
