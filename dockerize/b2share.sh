#!/bin/bash -e
# This file is supposed to live in a docker container

if [ ! -f /eudat/provisioned ]; then
    # this cannot be done while building the container
    # because it depends on another host: elasticsearch
    /usr/bin/b2share db create
    # FIXME: for now index init is not initializing properly the indices
    # /usr/bin/b2share index init
    /usr/bin/b2share schemas init

    # Load the demo config using staging B2Access Server if requested
    if [ "${LOAD_DEMO_CONFIG}" = "1" ]; then
        /usr/bin/b2share demo load_config
    fi

    /usr/bin/b2share demo load_data
    touch /eudat/provisioned
fi

if [ "${LOAD_DEMO_CONFIG}" = "1" ]; then
    export SSL_CERT_FILE="/eudat/b2share/staging_b2access.pem"
fi

/usr/bin/b2share run -h 0.0.0.0
