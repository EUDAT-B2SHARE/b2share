#!/bin/bash
# This file is supposed to live in a docker container

if [ ! -f /eudat/provisioned ]; then
    # this cannot be done while building the container
    # because it depends on another host: elasticsearch
    /usr/bin/b2share db create
    /usr/bin/b2share index init
    /usr/bin/b2share schemas init
    /usr/bin/b2share demo load_config
    /usr/bin/b2share demo load_data
    touch /eudat/provisioned
fi
/usr/bin/b2share run
