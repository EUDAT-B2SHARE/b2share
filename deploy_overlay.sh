#!/bin/sh

#I hate this overlay method, but it seems to be the way things are done.
#Note that files with the same name are overwritten so be careful to prefix
#files with name of module or similar scheme.

#Another thing to be careful of is to remove any moved or renamed files from
#the installation to avoid confusion later.

cp simplestore/lib/*.py /opt/invenio/lib/python/invenio/
cp -r simplestore/etc/static/* /opt/invenio/var/www/
cp -r simplestore/etc/templates/*.html /opt/invenio/etc/templates/
chown -R www-data.www-data /opt/invenio
service apache2 restart
