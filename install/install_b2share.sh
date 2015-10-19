#!/bin/bash

# # invoke with
# /vagrant/install_b2share.sh 2>&1 | tee install.log

MYSQL_ROOT=invenio
USER=vagrant
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

echo; echo "### Go to b2share"
source /usr/bin/virtualenvwrapper.sh
workon b2share
cdvirtualenv src/b2share

if [ ! -d "./invenio/b2share" ]; then
   echo "Error: b2share not present in the virtual environment"
   exit 1
fi

echo; echo "### Install pip dependencies"
pip install -q Babel honcho flower # flower is for monitoring celery tasks

echo; echo "### Install invenio egg"
pip install -q -e . --allow-all-external
pip install -q -e .[img]
if [ "$ENVIRONMENT" == "development" ]; then
  pip install -q -e .[development]
fi
cp -r ./invenio.egg-info ..

for f in requirements*.txt; do
   echo; echo "### pip install -r $f"
   pip install -q -r $f;
done

echo; echo "### Run npm install"
npm update
npm install
cp -r ./node_modules ..

echo; echo "### Make bower config"
inveniomanage bower -i bower-base.json > bower.json

echo; echo "### Run bower install"
bower install

echo; echo "### Collecting and building assets"
if [ "$ENVIRONMENT" == "development" ]; then
  inveniomanage config set COLLECT_STORAGE flask.ext.collect.storage.link
fi
inveniomanage collect
inveniomanage assets build

echo; echo "### Config secret"
# CFG_SITE_SECRET_KEY deprecated in favor of SECRET_KEY, create it here
inveniomanage config create secret-key

echo; echo "### Config lessc, cleancss, ..."
inveniomanage config set LESS_BIN `find $PWD/node_modules -iname lessc | head -1`
inveniomanage config set CLEANCSS_BIN `find $PWD/node_modules -iname cleancss | head -1`
inveniomanage config set REQUIREJS_BIN `find $PWD/node_modules -iname r.js | head -1`
inveniomanage config set UGLIFYJS_BIN `find $PWD/node_modules -iname uglifyjs | head -1`

echo; echo "### Config site name"
inveniomanage config set CFG_SITE_NAME B2Share
inveniomanage config set CFG_SITE_NAME_INTL "{u'en' : u'B2Share'}"
inveniomanage config set CFG_SITE_LANGS "[u'en']"
# for lang in af ar bg ca cs de el es fr hr gl ka it rw lt hu ja no pl pt ro ru sk sv uk zh_CN zh_TW; do
# 	inveniomanage config set CFG_SITE_NAME_INTL "{u'$lang' : u'B2Share'}"
# done

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
# another bibindex scheduling for global index because it is a virtual index
bibindex -w global -f50000 -s5m -uadmin

echo; echo "### Setup bibtasks: bibreformat"
bibreformat -oHB -s5m -uadmin

echo; echo "### Setup bibtasks: webcoll"
webcoll -v0 -s5m -uadmin

echo; echo "### Setup bibtasks: bibrank"
bibrank -f50000 -s5m -uadmin

echo; echo "### Setup bibtasks: bibsort"
bibsort -s5m -uadmin

if [ "$ENVIRONMENT" == "production" ]; then
  echo; echo "### Config for production"
   inveniomanage config set CFG_SITE_URL https://0.0.0.0
   inveniomanage config set CFG_SITE_SECURE_URL https://0.0.0.0
   inveniomanage config set CFG_EMAIL_BACKEND flask.ext.email.backends.smtp.Mail
   inveniomanage config set CFG_SITE_FUNCTION ""
else
  echo; echo "### Config for development"
   inveniomanage config set CFG_SITE_URL http://0.0.0.0:4000
   inveniomanage config set CFG_SITE_SECURE_URL http://0.0.0.0:4443
   inveniomanage config set CFG_EMAIL_BACKEND flask.ext.email.backends.dummy.Mail
   inveniomanage config set CFG_SITE_FUNCTION "Development Environment"
   inveniomanage config set DEBUG True
   inveniomanage config set DEBUG_TB_ENABLED False
   inveniomanage config set DEBUG_TB_INTERCEPT_REDIRECTS False
   # inveniomanage config set ASSETS_DEBUG True
fi

inveniomanage upgrader run
python invenio/b2share/upgrades/b2share_2015_06_23_create_domain_admin_groups.py
