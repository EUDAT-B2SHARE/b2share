#!/bin/bash -e

# Helper script in order to start separate celery containers, WITH secrets

sleep 5

WORKDIR=/eudat/b2share
LOGLEVEL=""

if [[ "${CELERY_DEBUG}" ]]; then
  LOGLEVEL="--loglevel=DEBUG"
fi

# Start celery if variables are set.
sleep 20
[[ ${CELERY_WORKER} ]] && /usr/local/bin/celery worker -E -A b2share.celery --workdir=${WORKDIR} ${LOGLEVEL}
[[ ${CELERY_BEAT} ]] && /usr/local/bin/celery beat -A b2share.celery --pidfile= --workdir=${WORKDIR} ${LOGLEVEL}
