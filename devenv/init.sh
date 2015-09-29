#!/bin/sh
SAFE_NAME='b2share_evo';
DOCKER_IP=`docker-machine ip b2share2`;

# cd $VIRTUAL_EN/src/b2share

# bower install

# cd $VIRTUAL_EN/src/invenio

# npm install
# LESS_BIN=`find $PWD/node_modules -iname lessc | head -1`
# CLEANCSS_BIN=`find $PWD/node_modules -iname cleancss | head -1`
# REQUIREJS_BIN=`find $PWD/node_modules -iname r.js | head -1`
# UGLIFYJS_BIN=`find $PWD/node_modules -iname uglifyjs | head -1`
# LESS_BIN=$LESS_BIN
# CLEANCSS_BIN=$CLEANCSS_BIN
# REQUIREJS_BIN=$REQUIREJS_BIN
# UGLIFYJS_BIN=$UGLIFYJS_BIN


cat > $VIRTUAL_ENV/var/invenio.base-instance/invenio.cfg <<END_CONFIG

CFG_EMAIL_BACKEND="flask_email.backends.console.Mail"
CFG_BIBSCHED_PROCESS_USER="$USER"
CFG_DATABASE_HOST="$DOCKER_IP"
CFG_DATABASE_NAME="$SAFE_NAME"
CFG_DATABASE_USER="$SAFE_NAME"
CFG_SITE_URL="http://localhost:4000"
CFG_SITE_SECURE_URL="http://localhost:4000"
CFG_REDIS_HOSTS={'default': [{'db': 0, 'host': '$DOCKER_IP', 'port': 6379}]}

END_CONFIG

# inveniomanage config set COLLECT_STORAGE flask_collect.storage.link
inveniomanage database init --user=root --yes-i-know
inveniomanage database recreate --yes-i-know

cat <<END_INSTRUCTIONS

# Now you can run in two different terminals
$ celery worker -E -A invenio_celery.celery --workdir=$VIRTUAL_ENV
# and
$ inveniomanage runserver

END_INSTRUCTIONS
