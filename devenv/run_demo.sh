#!/bin/bash

###############################################################################
# --- This script installs the development version of b2share2 ---
###############################################################################

### The following commands must be run beforehand
# brew install python --framework --universal
# pip install virtualenv virtualenvwrapper

if [ -n "$VIRTUAL_ENV" ]; then
	echo "Please deactivate the current virtual environment before running this script"
	echo "Virtual environment detected: $VIRTUAL_ENV"
	exit 1
fi

source /usr/local/bin/virtualenvwrapper.sh

export VIRTUALENV_NAME='b2share-evolution'
export DB_NAME='b2share-evolution'
export MACHINE_NAME=b2share

if [ "$1" = "--reinit" ]; then
	REINIT=1
fi

workon $VIRTUALENV_NAME
if [ $? -ne 0 ]; then
	echo; echo "### Make virtual env"
	# mkvirtualenv $VIRTUALENV_NAME
	mkvirtualenv --python=/usr/local/bin/python3 $VIRTUALENV_NAME
	workon $VIRTUALENV_NAME
	cdvirtualenv && mkdir src
	pip install --upgrade pip
fi

echo "### Prepare docker machine"
docker-machine start $MACHINE_NAME >/dev/null
if [ $? -ne 0 ]; then
	echo; echo "### Create docker machine for b2share"
	docker-machine create -d virtualbox $MACHINE_NAME
	docker-machine start $MACHINE_NAME
fi
eval $(docker-machine env $MACHINE_NAME)
DOCKER_IP=`docker-machine ip $MACHINE_NAME`

cdvirtualenv
export B2SHARE_UI_PATH=`pwd`/src/b2share/webui/app
export B2SHARE_BROKER_URL="redis://${DOCKER_IP}:6379/0"
export B2SHARE_ACCOUNTS_SESSION_REDIS_URL="redis://${DOCKER_IP}:6379/0"
export B2SHARE_CELERY_RESULT_BACKEND="redis://${DOCKER_IP}:6379/1"
export B2SHARE_SECRET_KEY=$(base64 /dev/urandom | tr -d '/+' | dd bs=32 count=1 2>/dev/null)
export B2SHARE_SEARCH_ELASTIC_HOSTS="${DOCKER_IP}:9200"
export B2SHARE_SERVER_NAME="localhost:5000"

cdvirtualenv src
if [ ! -d ./b2share ]; then
	echo; echo "### Clone b2share"
	git clone git@github.com:EUDAT-B2SHARE/b2share.git --branch evolution

	echo; echo "### pip install b2share"
	cdvirtualenv src/b2share
	pip install -r requirements.txt

	echo; echo "### pip install b2share demo"
	cdvirtualenv src/b2share/demo
	pip install -e .

	REINIT=1

	echo; echo "### Configure b2share webui"
	cdvirtualenv src/b2share/webui
	npm install
	node_modules/webpack/bin/webpack.js -p # pack for production
fi

cdvirtualenv src/b2share/devenv
echo; echo "### Run docker-compose detached mode"
docker-compose up -d

cdvirtualenv src/b2share
ps aux | grep -v grep | grep celeryd
if [ $? -ne 0 ]; then
	echo; echo "### Run celeryd in background"
	nohup celery worker -E -A b2share.celery -l INFO --workdir=$VIRTUAL_ENV &
	sleep 2 # give a bit of time to celery
fi

if [ -n "$REINIT" ]; then
	echo; echo "### Reinitialize database"
	b2share db destroy --yes-i-know
	b2share db create
	b2share index destroy --yes-i-know
	b2share index init
	b2share schemas init

	echo; echo "### Add demo config and objects"
	b2share demo load_config -f
	b2share demo load_data
fi

echo; echo "### Run b2share"
export SSL_CERT_FILE="staging_b2access.pem"
# return URL is configured to be http://localhost:5000/api/oauth/authorized/b2access/
export B2ACCESS_CONSUMER_KEY=b2share_demo
export B2ACCESS_SECRET_KEY=demo3b2share3beta
b2share --debug run
