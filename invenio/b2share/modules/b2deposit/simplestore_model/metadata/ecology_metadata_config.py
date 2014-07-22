from invenio.ext.sqlalchemy import db

domain = "Ecology"
table_name = 'ecology'
icon = 'icon-leaf'
# note that fields will need more stuff like validators later
fields = [{'name':'ecosystem',
           'display_text':'Ecosystem',
           'col_type':db.String(256),
           'mandatory':False,
           'extra':False}]
domaindesc = 'Ecology data.'