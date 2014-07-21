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

# set default path if none is set (in invenio-scripts)
if [ "$INVENIO_DIR" = "" ] && [ "$1" = "" ]; then
   INVENIO_DIR="/opt/invenio"
elif [ "$1" != "" ]; then
   INVENIO_DIR="$1"
fi
cp -vr simplestore/lib/* $INVENIO_DIR/lib/python/invenio/
cp -vr simplestore/etc/static/* $INVENIO_DIR/var/www/
cp -vr simplestore/etc/templates/*.html $INVENIO_DIR/etc/templates/
cp -vr simplestore/etc/templates/*.markdown $INVENIO_DIR/etc/templates/

# a quick hack for general modifications
# XXX: invenio update unsafe
if [ -f $INVENIO_DIR/lib/python/invenio/bibfield_functions/is_type_isbn_issn_unit_tests.py ];
  then rm -v $INVENIO_DIR/lib/python/invenio/bibfield_functions/is_type_isbn_issn_unit_tests.py*;
fi

# add invenio-specific overlay
cp -vf invenio/templates/* $INVENIO_DIR/etc/templates/
cp -vrf invenio/lib/* $INVENIO_DIR/lib/python/invenio/
cp -vrf invenio/etc/* $INVENIO_DIR/etc/
cp -vrf invenio/var/* $INVENIO_DIR/var/

chown -R $WWW_USER.$WWW_USER $INVENIO_DIR

pip install -r b2share_requirements.txt

service $WWW_SERVICE restart
