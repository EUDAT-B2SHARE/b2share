#!/bin/bash
#Note that if you change this you will also need to update the makefile
INVENIO_DIR=/opt/invenio
MYSQL_PASS="invenio"
WWW_USER=apache
WWW_SERVICE=httpd

echo "DANGER, WILL ROBINSON!

This script is designed to replace any existing Invenio install. It will drop
the old database and move the original invenio directory to a backup location.
As such, it is quite possible it will destroy the existing install and leave 
you with a non-functioning version of Invenio. Please read through this script
before running it, to make sure you are happy with what it is going to do.

You have been warned!

To run, put this script and invenio-local.conf in a directory containg the code
for the invenio version you want to install.
"

if [ "$(id -u)" != "0" ]; then
  echo "This script must be run as root" 1>&2
  exit 1
fi

if [ ! -f ./invenio-local.conf ]; then
  echo "Must have invenio-local.conf file in current dir" 1>&2
  exit 1
fi

confirm=true
if [ "$1" == "--no-confirm" ]; then
  confirm=false
fi

#This script will remove any existing invenio install then attempt to make
#and install the version in the current directory.
#BE VERY CAREFUL!


#TODO: Test INVENIO_DIR doesn't have ending slash
MV_DIR=$INVENIO_DIR$(date +"%d-%m-%y")
if $confirm ; then
  read -p "About to run mv '$INVENIO_DIR $MV_DIR'; hit ctrl-c to abort"
fi
if [ -d $MV_DIR ]; then
  if $confirm ; then
    read -p "Found existing dir at $MV_DIR - about to remove; ctrl-c to abort"
  fi
  rm -rf $MV_DIR
fi
mv $INVENIO_DIR $INVENIO_DIR$(date +"%d-%m-%y")
rm -f /usr/local/lib/python2.6/site-packages/invenio
rm -f /usr/lib/python2.6/site-packages/invenio

#Take down Apache
service $WWW_SERVICE stop
aclocal
automake -a
autoconf
./configure --prefix=$INVENIO_DIR
make

#Ok, should install to /opt/invenio by default
make install

# a break in the process requiring to create symlinks
ln -s $INVENIO_DIR/lib/python/invenio /usr/lib64/python2.6/site-packages/invenio
ln -s $INVENIO_DIR/lib/python/invenio /usr/lib/python2.6/site-packages/invenio

# we need to rerun make install once the symlink is in place
make install

# on debian the file is not moved into a correct place
#cp -vf modules/miscutil/lib/build/lib.linux-x86_64-2.6/invenio/intbitset.so /opt/invenio/lib/python/invenio/
#chown $WWW_USER:$WWW_USER /opt/invenio/lib/python/invenio/intbitset.so

make install-bootstrap
make install-mathjax-plugin
make install-jquery-plugins
make install-jquery-tokeninput
make install-plupload-plugin
make install-ckeditor-plugin
make install-pdfa-helper-files
make install-mediaelement
make install-solrutils
make install-js-test-driver

cp invenio-local.conf $INVENIO_DIR/etc/
chown -R $WWW_USER:$WWW_USER $INVENIO_DIR
if $confirm ; then
  read -p "About to drop invenio database; ctrl-c to abort"
fi
mysql -u root -p$MYSQL_PASS -e "drop database invenio;"
echo "Creating new DB"
mysql -u root -p$MYSQL_PASS -e "CREATE DATABASE invenio DEFAULT CHARACTER SET utf8;"
mysql -u root -p$MYSQL_PASS -e "GRANT ALL PRIVILEGES ON invenio.*  TO root@localhost IDENTIFIED BY '$MYSQL_PASS';"
# generate configuration file
sudo -u $WWW_USER $INVENIO_DIR/bin/inveniocfg --update-all

#Below line had problems for some reason, ending up putting default in
#sudo -u $WWW_USER /opt/invenio/bin/inveniocfg --create-secret-key
#sudo -u $WWW_USER $INVENIO_DIR/bin/inveniomanage database create
sudo -u $WWW_USER $INVENIO_DIR/bin/inveniocfg --create-tables --yes-i-know
sudo -u $WWW_USER $INVENIO_DIR/bin/inveniocfg --update-all
#not sure if below is implied by above
sudo -u $WWW_USER $INVENIO_DIR/bin/inveniocfg --update-config-py
sudo -u $WWW_USER $INVENIO_DIR/bin/inveniomanage bibfield config load
sudo -u $WWW_USER $INVENIO_DIR/bin/inveniocfg --load-webstat-conf
sudo -u $WWW_USER $INVENIO_DIR/bin/inveniomanage apache create-config
sudo -u $WWW_USER $INVENIO_DIR/bin/inveniocfg --update-all

# insert initial collection to the list
mysql invenio --password=$MYSQL_PASS < collections.sql

service $WWW_SERVICE start
