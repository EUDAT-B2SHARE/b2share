#!/bin/bash

sudo CFG_INVENIO_SRCDIR=/home/admin/src/invenio CFG_INVENIO_HOSTNAME=ss-dev.pdc CFG_INVENIO_DOMAINNAME=kth.se CFG_INVENIO_ADMIN=livenson@kth.se /home/admin/src/invenio-devscripts/invenio-recreate-demo-site  --yes-i-know
