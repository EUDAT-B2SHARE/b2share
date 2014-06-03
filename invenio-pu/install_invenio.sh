#!/bin/bash

# # invoke with
# /vagrant/install_invenio.sh 2>&1 | tee /vagrant/install.log

export MYSQL_ROOT=invenio
cd /vagrant

if [[ $EUID -eq 0 ]]; then
   echo "This script should not be run as root"
   exit 1
fi

export PATH="/opt/python-2.7.6/bin:/usr/local/bin:$PATH"
source /opt/python-2.7.6/bin/virtualenvwrapper.sh 

if [[ `which pip` != "/opt/python-2.7.6/bin/pip" ]]; then
   echo "!!! pip not installed or wrong path"
   exit 1
fi

echo; echo "### Make and switch to virtualenv invenio"
mkvirtualenv invenio
cdvirtualenv
mkdir src; cd src

echo; echo "### Clone invenio/pu sources"
export BRANCH=pu
git clone https://github.com/jirikuncar/invenio.git
cd invenio

echo; echo "### Install invenio/pu pip dependencies"
pip install Babel 
pip install flower # flower is for monitoring celery tasks
pip install -r requirements-img.txt

echo; echo "### Install invenio/pu"
pip install -e . --process-dependency-links --allow-all-external

echo; echo "### Run pybabel"
pybabel compile -fd invenio/base/translations/

echo; echo "### Run npm install"
npm install
echo; echo "### Run bower install"
bower install
echo; echo "### Run grunt"
grunt

echo; echo "### Run inveniomanage collect"
inveniomanage collect

echo; echo "### Run inveniomanage config secret"
inveniomanage config create secret-key

echo; echo "### Run inveniomanage config lessc and cleancss"
inveniomanage config set LESS_BIN `find $PWD/node_modules -iname lessc | head -1`
inveniomanage config set CLEANCSS_BIN `find $PWD/node_modules -iname cleancss | head -1`

echo; echo "### Run inveniomanage database"
inveniomanage database init --user=root --password=$MYSQL_ROOT --yes-i-know
inveniomanage database create
#inveniomanage demosite create

echo; echo "### Config for development"
inveniomanage config set CFG_EMAIL_BACKEND flask.ext.email.backends.console.Mail
inveniomanage config set CFG_BIBSCHED_PROCESS_USER vagrant
inveniomanage config set CFG_SITE_URL http://0.0.0.0:4000
inveniomanage config set CFG_DEVEL_SITE 9
inveniomanage config set CFG_DEVEL_TOOLS "['werkzeug-debugger', 'debug-toolbar']"

echo; echo "### Run celery"
celeryd -E -A invenio.celery.celery --workdir=$VIRTUAL_ENV

# inveniomanage runserver
