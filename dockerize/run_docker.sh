#!/bin/bash

export B2SHARE_SERVER_NAME=b2share2.localhost
echo "Important: \$B2SHARE_SERVER_NAME must have the same value as the Host header set in nginx, see b2share.conf for line:"
echo "'proxy_set_header Host ...'"
echo ""
echo "You might also need to edit your /etc/hosts file, e.g. add a line (with the real value substituted in) like this:"
echo "'192.168.99.100  \$B2SHARE_SERVER_NAME'"
echo ""
echo "The current configuration is: "
echo B2SHARE_SERVER_NAME=$B2SHARE_SERVER_NAME
echo ""
echo "After install, B2SHARE will become available at:   https://$B2SHARE_SERVER_NAME"
echo ""
read -n1 -r -p "Press any key to start... "

export MACHINE_NAME=b2sharebeta
docker-machine start $MACHINE_NAME >/dev/null 2>/dev/null
if [ $? -ne 0 ]; then
	docker-machine create -d virtualbox $MACHINE_NAME
fi

eval "$(docker-machine env $MACHINE_NAME)"
docker-compose up -d
docker-compose logs -f b2share
