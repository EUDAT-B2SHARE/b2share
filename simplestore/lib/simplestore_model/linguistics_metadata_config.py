from invenio.sqlalchemyutils import db


domain = "Linguistics"
table_name = 'linguistics'
icon = 'icon-quote-right'
# note that fields will need more stuff like validators later
fields = [{'name':'phrase_popularity',
           'display_text':'Phrase Popularity',
           'col_type':db.String(256),
           'mandatory':False,
           'extra':False}]
