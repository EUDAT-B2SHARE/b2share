#!/bin/sh

# Note that files with the same name are overwritten so be careful to prefix
# files with name of module or similar scheme.

# Another thing to be careful of is to remove any moved or renamed files from
# the installation to avoid confusion later. And don't forgot the damned .pyc
# files.

#apache on redhat and derivatives, www-data on debian
WWW_USER=www-data

#httpd on redhat and derivatives, apache2 on debian
WWW_SERVICE=apache2

cp -vr simplestore/lib/* /opt/invenio/lib/python/invenio/
cp -vr simplestore/etc/static/* /opt/invenio/var/www/
cp -vr simplestore/etc/templates/*.html /opt/invenio/etc/templates/
chown -R $WWW_USER.$WWW_USER /opt/invenio

#The following vars should be set in invenio-local.conf.
#I used to do it here with "echo bla >>" but it was a horrible hack
#left here for documentation purposes until proper solution
#CFG_ACCESS_CONTROL_NOTIFY_USER_ABOUT_NEW_ACCOUNT = 1
#CFG_SIMPLESTORE_UPLOAD_FOLDER = /opt/invenio/var/tmp/simplestore_uploads
#CFG_SITE_NAME = SimpleStore
#CFG_WEBSTYLE_TEMPLATE_SKIN = openaire
#sudo -u www-data /opt/invenio/bin/inveniocfg --update-all


# a quick hack for general modifications
# XXX: invenio update unsafe
if [ -f /opt/invenio/lib/python/invenio/bibfield_functions/is_type_isbn_issn_unit_tests.py ];
  then rm -v /opt/invenio/lib/python/invenio/bibfield_functions/is_type_isbn_issn_unit_tests.py*;
fi
cp -vf invenio/templates/* /opt/invenio/etc/templates/
cp -vrf invenio/lib/* /opt/invenio/lib/python/invenio/
cp -vrf invenio/etc/* /opt/invenio/etc/

service $WWW_SERVICE restart
