#!/bin/bash
SOURCE=../../b2share/
TARGET=/home/vagrant/.virtualenvs/b2share/src/
HOST=default
echo "Copying $SOURCE to $HOST:$TARGET"
scp -q -F .sshconfig -r $SOURCE vagrant@$HOST:$TARGET
