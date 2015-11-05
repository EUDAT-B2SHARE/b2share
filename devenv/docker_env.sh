#!/bin/sh
SAFE_NAME='b2share_evo';
DOCKER_IP=`docker-machine ip b2share`;

export B2SHARE_BROKER_URL="redis://${DOCKER_IP}:6379/0"
export B2SHARE_CELERY_RESULT_BACKEND="redis://${DOCKER_IP}:6379/1"
export B2SHARE_SECRET_KEY=$(base64 /dev/urandom | tr -d '/+' | dd bs=32 count=1 2>/dev/null)
