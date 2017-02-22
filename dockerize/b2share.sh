#!/bin/bash -e
# This file is supposed to live in a docker container

if [ ! -f /eudat/provisioned ]; then
    if [ "${INIT_DB_AND_INDEX}" = "1" ]; then
        # this cannot be done while building the container
        # because it depends on another host: elasticsearch
        /usr/bin/b2share db create
        # FIXME: for now index init is not initializing properly the indices
        /usr/bin/b2share index init
        /usr/bin/b2share schemas init
    fi

    # if a config file already exists, continue
    /usr/bin/b2share demo load_config || true

    if [ "${LOAD_DEMO_COMMUNITIES_AND_RECORDS}" = "1" ]; then
        /usr/bin/b2share demo load_data
    fi

    touch /eudat/provisioned
fi

if [ "${USE_STAGING_B2ACCESS}" = "1" ]; then
    export SSL_CERT_FILE="/eudat/b2share/staging_b2access.pem"
fi

/usr/bin/supervisord
