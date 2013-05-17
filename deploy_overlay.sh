#!/bin/sh

# Note that files with the same name are overwritten so be careful to prefix
# files with name of module or similar scheme.

# Another thing to be careful of is to remove any moved or renamed files from
# the installation to avoid confusion later. And don't forgot the damned .pyc
# files.

cp -v simplestore/lib/*.py /opt/invenio/lib/python/invenio/
cp -vr simplestore/etc/static/* /opt/invenio/var/www/
cp -vr simplestore/etc/templates/*.html /opt/invenio/etc/templates/
chown -R www-data.www-data /opt/invenio

# branding adjustments
sed -i 's#<title>.*</title>#<title>EUDAT SimpleStore</title>#' /opt/invenio/etc/templates/page.html

# a quick hack for title replacement
cp -vf invenio/templates/*  /opt/invenio/etc/templates/

service apache2 restart
