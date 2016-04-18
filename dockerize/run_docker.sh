#!/bin/bash

export MACHINE_NAME=b2sharebeta1

docker-machine start $MACHINE_NAME >/dev/null 2>/dev/null
if [ $? -ne 0 ]; then
	docker-machine create -d virtualbox $MACHINE_NAME
fi

eval "$(docker-machine env $MACHINE_NAME)"
export B2SHARE_SERVER_NAME="$(docker-machine ip $MACHINE_NAME)"
echo B2SHARE_SERVER_NAME=$B2SHARE_SERVER_NAME
docker-compose up -d

echo
echo "B2SHARE should soon become available at:   http://$B2SHARE_SERVER_NAME:5000"
