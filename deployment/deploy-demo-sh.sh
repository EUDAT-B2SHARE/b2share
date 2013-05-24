#!/bin/bash

# update simplestore and invenio repos
/home/admin/src/invenio-devscripts/recreate.demo.sh

echo "========== DONE =========="

/etc/init.d/apache2 restart

sudo -u www-data /opt/invenio/bin/bibindex -u admin
sudo -u www-data /opt/invenio/bin/webcoll -u admin

# make it periodic
sudo -u www-data /opt/invenio/bin/webcoll -v0 -s1m -u admin
sudo -u www-data /opt/invenio/bin/bibindex -u admin f50000 -s1m

