#!/bin/bash

PYPATH=/opt/python-2.7.6

echo; echo "### Setup iptables to redirect 4443 to 4000 (sudo!)"
sudo iptables -t nat -F # clean up tables!
sudo iptables -A PREROUTING -t nat -i eth0 -p tcp --dport 4443 -j REDIRECT --to-port 4000

source $WORKON_HOME/b2share/bin/activate
cd $WORKON_HOME/b2share

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

echo; echo "### Run invenio server"
inveniomanage runserver -d -r
