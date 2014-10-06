#!/bin/bash

# # invoke with
# /vagrant/install_b2share.sh 2>&1 | tee install.log

MYSQL_ROOT=invenio
USER=vagrant
PYPATH=/opt/python-2.7.6
BRANCH=master

if [[ $EUID -eq 0 ]]; then
   echo "This script should not be run as root"
   exit 1
fi

ENVIRONMENT=$1
if [ "$ENVIRONMENT" != "production" ]  && [ "$ENVIRONMENT" != "development" ]; then
   echo "Usage: install_b2share.sh production|development"
   exit 1
fi

export PATH="$PYPATH/bin:$PATH"
source $PYPATH/bin/virtualenvwrapper.sh

if [[ `which pip` != "$PYPATH/bin/pip" ]]; then
   echo "!!! pip not installed or wrong path"
   exit 1
fi

echo; echo "### Make and switch to virtualenv b2share"
mkvirtualenv b2share
cdvirtualenv
mkdir src; cd src

echo; echo "### Clone b2share/b2share"
if [ "$ENVIRONMENT" == "production" ]; then
   git clone -b $BRANCH https://github.com/b2share/b2share.git
else
   echo "*** Expecting b2share to be already cloned and mapped via Vagrantfile: synced_folder"
fi
cd b2share

echo; echo "### Install pip dependencies"
pip install Babel
pip install flower # flower is for monitoring celery tasks
pip install -r requirements-img.txt
pip install -r requirements-b2share.txt

echo; echo "### Install invenio egg"
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
# CFG_SITE_SECRET_KEY deprecated in favor of SECRET_KEY, create it here
inveniomanage config create secret-key

echo; echo "### Run inveniomanage config lessc and cleancss"
inveniomanage config set LESS_BIN `find $PWD/node_modules -iname lessc | head -1`
inveniomanage config set CLEANCSS_BIN `find $PWD/node_modules -iname cleancss | head -1`

echo; echo "### Config site name"
inveniomanage config set CFG_SITE_NAME B2Share
inveniomanage config set CFG_SITE_NAME_INTL "{u'en' : u'B2Share'}"
inveniomanage config set CFG_SITE_LANGS "[u'en']"
for lang in af ar bg ca cs de el es fr hr gl ka it rw lt hu ja no pl pt ro ru sk sv uk zh_CN zh_TW; do
	inveniomanage config set CFG_SITE_NAME_INTL "{u'$lang' : u'B2Share'}"
done

echo; echo "### Config bibsched user"
inveniomanage config set CFG_BIBSCHED_PROCESS_USER $USER

#echo; echo "### Config database"
#inveniomanage config set CFG_DATABASE_HOST localhost
#inveniomanage config set CFG_DATABASE_NAME invenio
#inveniomanage config set CFG_DATABASE_USER root
#inveniomanage config set CFG_DATABASE_PASS invenio

echo; echo "### Config emails"
inveniomanage config set CFG_SITE_ADMIN_EMAIL admin@localhost
inveniomanage config set CFG_SITE_SUPPORT_EMAIL admin@localhost
inveniomanage config set CFG_WEBALERT_ALERT_ENGINE_EMAIL admin@localhost
inveniomanage config set CFG_WEBCOMMENT_ALERT_ENGINE_EMAIL admin@localhost

echo; echo "### Config upload folder"
inveniomanage config set CFG_B2SHARE_UPLOAD_FOLDER /tmp/ss/

echo; echo "### Config B2SHARE domains"
inveniomanage config set CFG_B2SHARE_DOMAINS "generic, drihm, linguistics, euon, bbmri"

echo; echo "### Config epic credentials"
inveniomanage config set CFG_EPIC_USERNAME ""
inveniomanage config set CFG_EPIC_PASSWORD ""
inveniomanage config set CFG_EPIC_BASEURL ""
inveniomanage config set CFG_EPIC_PREFIX ""

echo; echo "### Config captcha keys"
inveniomanage config set CFG_CAPTCHA_PRIVATE_KEY ""
inveniomanage config set CFG_CAPTCHA_PUBLIC_KEY ""

echo; echo "### Run inveniomanage database"
# needs to be run after the site name is set (root collection is CFG_SITE_NAME)
inveniomanage database init --user=root --password=$MYSQL_ROOT --yes-i-know
inveniomanage database create

echo; echo "### Setup database collections"
mysql -u root -D invenio --password=$MYSQL_ROOT < `dirname $0`/_collections.sql
GRANT="GRANT ALL PRIVILEGES ON invenio.* TO 'root'@'%' IDENTIFIED BY '$MYSQL_ROOT';"
mysql -u root --database=invenio --password=$MYSQL_ROOT -e "$GRANT"

echo; echo "### Setup bibtasks: bibindex"
bibindex -f50000 -s5m -uadmin

echo; echo "### Setup bibtasks: bibreformat"
bibreformat -oHB -s5m -uadmin

echo; echo "### Setup bibtasks: webcoll"
webcoll -v0 -s5m -uadmin

echo; echo "### Setup bibtasks: bibrank"
bibrank -f50000 -s5m -uadmin

echo; echo "### Setup bibtasks: bibsort"
bibsort -s5m -uadmin

echo; echo "### Config for development"
if [ "$ENVIRONMENT" == "production" ]; then
   inveniomanage config set CFG_SITE_URL https://0.0.0.0
   inveniomanage config set CFG_SITE_SECURE_URL https://0.0.0.0
   inveniomanage config set CFG_EMAIL_BACKEND flask.ext.email.backends.smtp.Mail
   inveniomanage config set CFG_SITE_FUNCTION ""
else
   inveniomanage config set CFG_SITE_URL http://0.0.0.0:4000
   inveniomanage config set CFG_SITE_SECURE_URL http://0.0.0.0:4443
   inveniomanage config set CFG_EMAIL_BACKEND flask.ext.email.backends.dummy.Mail
   inveniomanage config set CFG_SITE_FUNCTION "Development Environment"
   inveniomanage config set DEBUG True
   inveniomanage config set ASSETS_DEBUG True
fi
