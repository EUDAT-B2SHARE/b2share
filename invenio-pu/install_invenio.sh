#!/bin/bash

# # invoke with
# sudo PATH="/opt/python-2.7.6/bin:$PATH" /vagrant/install_invenio.sh 2>&1 | tee /vagrant/install.log

export MYSQL_ROOT=invenio
cd /vagrant

if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root"
   exit 1
fi

echo; echo "### Start mysql"
chkconfig mysqld on
service mysqld start
mysqladmin -u root password $MYSQL_ROOT

echo; echo "### Start redis"
chkconfig redis on
service redis start

echo; echo "### Clone invenio/pu sources"
export BRANCH=pu
git clone https://github.com/jirikuncar/invenio.git
cd invenio

echo; echo "### Install invenio/pu pip dependencies"
pip install -r requirements-img.txt

echo; echo "### Install invenio/pu"
pip install -e . --process-dependency-links --allow-all-external

echo; echo "### Run pybabel"
pybabel compile -fd invenio/base/translations/

echo; echo "### Install npm"
npm install
npm install -g grunt-cli bower
echo; echo "### Install bower"
bower --allow-root install
echo; echo "### Run grunt"
grunt

echo; echo "### Run inveniomanage collect"
inveniomanage collect

echo; echo "### Run inveniomanage config"
inveniomanage config create secret-key
inveniomanage config set LESS_BIN `find $PWD/node_modules -iname lessc | head -1`
inveniomanage config set CLEANCSS_BIN `find $PWD/node_modules -iname cleancss | head -1`

echo; echo "### Run inveniomanage database"
inveniomanage database init --user=root --password=$MYSQL_ROOT --yes-i-know
inveniomanage database create
#inveniomanage demosite create

echo; echo "### Run celery"
celery worker -E -A invenio.celery

echo; echo "### Config for development"
inveniomanage config set CFG_EMAIL_BACKEND flask.ext.email.backends.console.Mail
inveniomanage config set CFG_BIBSCHED_PROCESS_USER vagrant
inveniomanage config set CFG_SITE_URL http://0.0.0.0:4000

echo; echo "### RUN SERVER"
chown -R vagrant:vagrant /opt/python-2.7.6
#inveniomanage runserver
