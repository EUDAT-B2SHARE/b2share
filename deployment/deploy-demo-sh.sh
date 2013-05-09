#!/bin/bash

# update simplestore and invenio repos
/home/admin/src/invenio-devscripts/recreate.demo.sh

echo "========== DONE =========="

/etc/init.d/apache2 restart

sudo -u www-data /opt/invenio/bin/bibindex -u admin
sudo -u www-data /opt/invenio/bin/webcoll -u admin
