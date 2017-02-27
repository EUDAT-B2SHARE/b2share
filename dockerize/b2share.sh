#!/bin/bash -e
# This file is supposed to live in a docker container

if [ ! -f /usr/var/b2share-instance/provisioned ]; then

    # if a config file already exists, continue
    /usr/bin/b2share demo load_config || true

    # wait for all the services to start
    # FIXME: we should have some shell code to check that instead of a sleep.
    sleep 30
    if [ "${INIT_DB_AND_INDEX}" = "1" ]; then
        /usr/bin/b2share index queue init
        /usr/bin/b2share db init
        /usr/bin/b2share db create
        # FIXME: for now index init is also creating unused invenio indices
        /usr/bin/b2share index init
        /usr/bin/b2share schemas init
        sleep 20
    fi

    if [ "${LOAD_DEMO_COMMUNITIES_AND_RECORDS}" = "1" ]; then
        /usr/bin/b2share demo load_data
    fi

    touch /usr/var/b2share-instance/provisioned
fi

if [ "${USE_STAGING_B2ACCESS}" = "1" ]; then
    export SSL_CERT_FILE="/eudat/b2share/staging_b2access.pem"
fi

/usr/bin/supervisord
