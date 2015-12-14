from invenio_ext.sqlalchemy import db
from datetime import date

domain = 'NRM'
# display_name = 'Herbarium Crowdsourcing Initiative'
display_name = 'Herbarium'
table_name = 'NRM'
image = 'domain-nrm.png'
kind = 'project'
domaindesc = 'Herbarium data.'

fields = [
    {
        'name': 'uuid',
        'col_type': db.String(256),
        'display_text': 'UUID',
        'description': "The unique identifier for the herbarium sheet shown in this image, "
                       "typically corresponds to the herbarium sheet's catalogue number shown on the label.",
        'required': True
    },
    {
        'name': 'species_name',
        'col_type': db.String(256),
        'display_text': 'Species name',
        'description': 'Species name displayed on the herbarium sheet label.',
        'required': True
    },
    {
        'name': 'collector_name',
        'col_type': db.String(256),
        'display_text': 'Collector name',
        'description': 'Name of the collector shown on the label.',
        'required': True
    },
    {
        'name': 'collection_date',
        'col_type': db.Date(),
        'display_text': 'Collection date',
        'description': 'Collection date shown on the label. This may be incomplete and/or show only year or year/month.',
        'required': True,
        'default': date.today()
    },
    {
        'name': 'locality',
        'col_type': db.String(256),
        'display_text': 'Locality',
        'description': 'Location at which the item shown in the image was collected. '
                       'This may range from a country name to specific place names and descriptions.',
        'required': True
    },
    {
        # TODO: Should be joined w/ 'longitude'
        'name': 'latitude',
        'col_type': db.String(256),
        'display_text': 'Latitude',
        'description': 'Only modern labels will typically carry coordinates.',
        'required': False
    },
    {
        # TODO: Should be joined w/ 'latitude'
        'name': 'longitude',
        'col_type': db.String(256),
        'display_text': 'Longitude',
        'description': 'Only modern labels will typically carry coordinates.',
        'required': False
    },
]
