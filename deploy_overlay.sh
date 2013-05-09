#!/bin/sh

#Note that files with the same name are overwritten so be careful to prefix
#files with name of module or similar scheme.

#Another thing to be careful of is to remove any moved or renamed files from
#the installation to avoid confusion later.

cp -v simplestore/lib/*.py /opt/invenio/lib/python/invenio/
cp -vr simplestore/etc/static/* /opt/invenio/var/www/
cp -vr simplestore/etc/templates/*.html /opt/invenio/etc/templates/
chown -R www-data.www-data /opt/invenio
service apache2 restart
