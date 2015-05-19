#!/bin/bash

PYPATH=/opt/python-2.7.6

echo; echo "### Setup iptables to redirect 4443 to 4000 (sudo!)"
sudo iptables -t nat -F # clean up tables!
sudo iptables -A PREROUTING -t nat -p tcp --dport 4443 -j REDIRECT --to-port 4000

source $WORKON_HOME/b2share/bin/activate
cd $WORKON_HOME/b2share

if [ ! -d "./src/b2share/invenio.egg-info" ]; then
	echo; echo "### Restoring invenio.egg-info"
	cp -r ./src/invenio.egg-info ./src/b2share/
fi
if [ ! -d "./src/b2share/node_modules" ]; then
	echo; echo "### Restoring node_modules"
	cp -r ./src/node_modules ./src/b2share/
fi

# bibsched.pid
echo; echo "### Run bibsched"
mkdir -p $WORKON_HOME/b2share/var/run
$WORKON_HOME/b2share/bin/bibsched restart

ps aux | grep -v grep | grep celeryd
if [ $? -ne 0 ]; then
	echo; echo "### Run celeryd"
	nohup celeryd -E -A invenio.celery.celery --workdir=$VIRTUAL_ENV &
	sleep 1 # give a bit of time to celery
fi

echo; echo "### Preloading assets"
inveniomanage collect

echo; echo "### Run invenio server"
inveniomanage runserver -d -r
