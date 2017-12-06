#!/bin/bash -e
# This file is supposed to live in a docker container

# wait for all the services to start
# FIXME: we should have some shell code to check that instead of a sleep.
sleep 30

if [ ! -f /usr/var/b2share-instance/provisioned ]; then

    # if a config file already exists, continue
    /usr/bin/b2share demo load_config || true

    if [ "${INIT_DB_AND_INDEX}" = "1" ]; then
        /usr/bin/b2share db init
        /usr/bin/b2share upgrade run -v
        sleep 20
    fi

    if [ "${LOAD_DEMO_COMMUNITIES_AND_RECORDS}" = "1" ]; then
        /usr/bin/b2share demo load_data
    elif [ "${INIT_DB_AND_INDEX}" = "1" ]; then
        # add default location
        /usr/bin/b2share files add-location 'local' file:///usr/var/b2share-instance/files --default
    fi

    touch /usr/var/b2share-instance/provisioned
fi

if [ "${USE_STAGING_B2ACCESS}" = "1" ]; then
    export SSL_CERT_FILE="/eudat/b2share/staging_b2access.pem"
fi

# safe to run even when up to date
/usr/bin/b2share upgrade run -v

/usr/bin/supervisord
