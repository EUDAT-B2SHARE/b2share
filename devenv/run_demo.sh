#!/bin/sh

###############################################################################
# --- This script installs the development version of b2share2 ---
###############################################################################

### The following commands must be run beforehand
# brew install python --framework --universal
# pip install virtualenv
# pip install virtualenvwrapper

source /usr/local/bin/virtualenvwrapper.sh

export VIRTUALENV_NAME='b2share-evolution'
export DB_NAME='b2share-evolution'
export MACHINE_NAME=b2share

#deactivate if we're already in a virtual env
deactivate

workon $VIRTUALENV_NAME
if [ $? -ne 0 ]; then
	echo; echo "### Make virtual env"
	mkvirtualenv $VIRTUALENV_NAME
	workon $VIRTUALENV_NAME
	cdvirtualenv && mkdir src
fi

docker-machine start $MACHINE_NAME
if [ $? -ne 0 ]; then
	echo; echo "### Create docker machine for b2share"
	docker-machine create -d virtualbox $MACHINE_NAME
	docker-machine start $MACHINE_NAME
fi
eval $(docker-machine env $MACHINE_NAME)
DOCKER_IP=`docker-machine ip $MACHINE_NAME`


cdvirtualenv src
if [ ! -d ./ui-frontend ]; then
	echo; echo "### Clone b2share UI"
	git clone git@github.com:EUDAT-B2SHARE/ui-frontend.git
	cd ui-frontend
	npm install
fi


cdvirtualenv src
if [ ! -d ./b2share ]; then
	echo; echo "### Clone b2share"
	git clone git@github.com:EUDAT-B2SHARE/b2share.git --branch evolution

	echo; echo "### pip install b2share"
	cd b2share
	pip install -r requirements.txt

	echo; echo "### Configure b2share"
	cp devenv/b2share.cfg ../../var/b2share-instance/
	python manage.py db init
	python manage.py db create
fi

cdvirtualenv src
export B2SHARE_UI_PATH=`pwd`/ui-frontend/app
export B2SHARE_BROKER_URL="redis://${DOCKER_IP}:6379/0"
export B2SHARE_CELERY_RESULT_BACKEND="redis://${DOCKER_IP}:6379/1"
export B2SHARE_SECRET_KEY=$(base64 /dev/urandom | tr -d '/+' | dd bs=32 count=1 2>/dev/null)

cdvirtualenv src/b2share/devenv
echo; echo "### Run docker-compose detached mode"
docker-compose up -d

cdvirtualenv src/b2share
ps aux | grep -v grep | grep celeryd
if [ $? -ne 0 ]; then
	echo; echo "### Run celeryd in background"
	nohup celery worker -E -A b2share.celery -l INFO --workdir=$VIRTUAL_ENV &
	sleep 1 # give a bit of time to celery
fi

cdvirtualenv src/b2share
echo; echo "### Run b2share"
python manage.py --debug run
