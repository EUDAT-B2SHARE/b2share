#!/bin/sh

###############################################################################
# This script describes the steps to take in order to start b2share2
# Commented out are the installation commands (please run them manually)
#
# The script makes a python virtual env and clones b2share2 and ui-frontend
# into it; then makes a docker machine to host the elasticsearch, redis,
# and all the other docker containers needed by invenio. It also uses the
# init.sh script that configures the b2share2 installation
###############################################################################

# brew install python --framework --universal
# pip install virtualenv
# pip install virtualenvwrapper

export WORKON_HOME=~/.virtualenvs
source /usr/local/bin/virtualenvwrapper.sh

# mkvirtualenv b2share-evolution
workon b2share-evolution

# cdvirtualenv && mkdir src

# cdvirtualenv src
# git clone git@github.com:EUDAT-B2SHARE/b2share.git --branch evolution
# git clone git@github.com:EUDAT-B2SHARE/ui-frontend.git
# cdvirtualenv src/b2share
# pip install -r requirements.txt
# ln -s $WORKON_HOME/b2share-evolution/src/ui-frontend $WORKON_HOME/b2share-evolution/var/invenio.base-instance/static/

# cdvirtualenv src/ui-frontend/
# npm install

# cdvirtualenv src/b2share
cdvirtualenv src/b2share/devenv
# docker-machine create -d virtualbox b2share2
docker-machine start b2share2
eval $(docker-machine env b2share2)

echo; echo "### Run docker-compose"
nohup docker-compose up &
sleep 5

# ./init.sh

ps aux | grep -v grep | grep celeryd
if [ $? -ne 0 ]; then
	echo; echo "### Run celeryd"
	nohup celery worker -E -A invenio_celery.celery --workdir=$VIRTUAL_ENV &
	sleep 1 # give a bit of time to celery
fi

inveniomanage runserver
