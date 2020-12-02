#!/bin/bash -e
# This file is supposed to live in a docker container

# wait for all the services to start
# FIXME: we should have some shell code to check that instead of a sleep.
sleep 30

if [ ! -f /usr/var/b2share-instance/provisioned ]; then

    # if a config file already exists, continue
    /usr/local/bin/b2share demo load_config || true

    if [ "${INIT_DB_AND_INDEX}" = "1" ]; then
        /usr/local/bin/b2share db init
        /usr/local/bin/b2share upgrade run -v
        sleep 20
    fi

    if [ "${LOAD_DEMO_COMMUNITIES_AND_RECORDS}" = "1" ]; then
        /usr/local/bin/b2share demo load_data
    elif [ "${INIT_DB_AND_INDEX}" = "1" ]; then
        # add default location
        /usr/local/bin/b2share files add-location 'local' file:///usr/var/b2share-instance/files --default
    fi

    touch /usr/var/b2share-instance/provisioned
fi

# safe to run even when up to date
/usr/local/bin/b2share upgrade run -v

/usr/bin/supervisord
