from invenio.sqlalchemyutils import db

from datetime import date


domain = "euon"
display_name = "Ontology"
table_name = 'EUON'
image = 'domain-euon.png'
kind = 'project'


# note that fields will need more stuff like validators later
fields = [
          {'name': 'hasDomain',
           'col_type': db.String(256),
           'display_text': 'Ontology Domain',
           'description': 'A category that describes the ontology, from a pre-defined list of categories',
           'required': True},
          {'name': 'hasOntologyLanguage',
           'col_type': db.String(256),
           'display_text': 'Ontology Language',
           'data_provide': 'select',
           'data_source': ['F-Logic',
                           'KIF',
                           'LexGrid-XML',
                           'OCML',
                           'OBO',
                           'OMV:DAML-OIL',
                           'OMV:OWL',
                           'OMV:OWL-DL',
                           'OMV:OWL-Full',
                           'OMV:OWL-Lite',
                           'OMV:RDF-S',
                           'Protégé-Frames',
                           'RRF',
                           'W3C:OWL_2',
                           'W3C:SKOS'],
           'other': 'Other...',
           'description': 'The language in which the ontology was developed',
           'required': True},
          {'name': 'usedOntologyEngineeringTool',
           'col_type': db.String(256),
           'display_text': 'Ontology Engineering Tool',
           'data_provide': 'select',
           'data_source': ['Protégé',
                           'Swoop',
                           'TopBraid Composer',
                           'OBO-Edit',
                           'OntoStudio',
                           'KAON',
                           'PoolParty Thesaurus Server'],
           'other': 'Other...',
           'description': 'The tool that was used to develop the ontology',
           'required': False},
          {'name': 'creationDate',
           'col_type': db.Date(),
           'display_text': 'Creation Date',
           'required': False},
          {'name': 'modificationDate',
           'col_type': db.Date(),
           'display_text': 'Modification Date',
           'required': False},
         ]
