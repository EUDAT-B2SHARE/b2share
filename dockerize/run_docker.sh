#!/bin/bash

export MACHINE_NAME=b2sharebeta1

docker-machine start $MACHINE_NAME >/dev/null 2>/dev/null
if [ $? -ne 0 ]; then
	docker-machine create -d virtualbox $MACHINE_NAME
fi

eval "$(docker-machine env $MACHINE_NAME)"
docker-compose up
