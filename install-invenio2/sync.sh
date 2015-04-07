#!/bin/bash
HOST=default

SOURCE=../../b2share/
TARGET=/home/vagrant/.virtualenvs/b2share/src/
echo "Copying $SOURCE to $HOST:$TARGET"
scp -q -F .sshconfig -r $SOURCE vagrant@$HOST:$TARGET

SOURCE=../install-invenio2/start_b2share.sh
TARGET=/vagrant
echo "Copying $SOURCE to $HOST:$TARGET"
scp -q -F .sshconfig $SOURCE vagrant@$HOST:$TARGET
