#!/bin/sh

# Note that files with the same name are overwritten so be careful to prefix
# files with name of module or similar scheme.

# Another thing to be careful of is to remove any moved or renamed files from
# the installation to avoid confusion later. And don't forgot the damned .pyc
# files.

cp -vr simplestore/lib/* /opt/invenio/lib/python/invenio/
cp -vr simplestore/etc/static/* /opt/invenio/var/www/
cp -vr simplestore/etc/templates/*.html /opt/invenio/etc/templates/
chown -R www-data.www-data /opt/invenio

# branding adjustments
sed -i 's#<title>.*</title>#<title>EUDAT SimpleStore</title>#' /opt/invenio/etc/templates/page.html

echo "CFG_SIMPLESTORE_UPLOAD_FOLDER = /opt/invenio/var/tmp/simplestore_uploads" >> /opt/invenio/etc/invenio-local.conf
sudo -u www-data /opt/invenio/bin/inveniocfg --update-all

# a quick hack for general modifications
# XXX: invenio update unsafe
cp -vf invenio/templates/* /opt/invenio/etc/templates/
cp -vf invenio/lib/* /opt/invenio/lib/python/invenio/

service apache2 restart
