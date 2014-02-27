#!/bin/bash 

# This script will install B2SHARE from scratch on a centos 6.5 x64 machine
# It uses invenio and B2SHARE sources from github
# It also uses the scripts in the invenio-scripts repository
# Running the script takes close to 2 hours (installs many packages)
# SEE ALSO the text at the end of this script

echo "************ Stopping firewall"
/sbin/service iptables stop
/sbin/chkconfig iptables off

echo "************ Installing wget & git"
yum install -y wget git 

echo "************ Git clone invenio"
git clone https://github.com/B2SHARE/invenio.git

echo "************ Git clone invenio-scripts"
git clone https://github.com/B2SHARE/invenio-scripts.git

echo "************ Git clone b2share"
git clone https://github.com/B2SHARE/b2share.git

echo "************ Git clone b2share.wiki"
git clone https://github.com/B2SHARE/b2share.wiki.git

echo "************ Installing required OS dependencies"
./invenio-scripts/install/install-invenio-deps-rh.sh

echo "************ Installing invenio base"
cp invenio-scripts/install/invenio-local.conf invenio/
(cd invenio && ../invenio-scripts/install/wipe-and-install-invenio-rh.sh --no-confirm)

echo "************ Deploying b2share overlay"
(cd b2share && ./deployment/deploy_overlay-rh.sh)

echo "************ Deploying b2share document files"
(cd b2share && ./deployment/update-help.sh)

echo "************ Starting invenio processes"
./invenio-scripts/install/start-daemons-rh.sh
# For guest user garbage­collector, you need also this:
sudo -u apache /opt/invenio/bin/inveniogc -guests -s5m -uadmin

echo "************ Installation done"
date > /etc/provisioned_at


echo 
echo "*** If you are configuring a development environment, you should:"
echo "    1. disable the redis cache:"
echo '       edit /opt/invenio/lib/python/invenio/config.py and set CFG_FLASK_CACHE_TYPE = "null"'
echo "    2. reduce the number of apache processes:"
echo '       edit /opt/invenio/etc/apache/invenio-apache-vhost.conf and replace "processes=5" with "processes=1"'
echo '    Restart'
echo '    3. configure invenio processes to run automatically: '
echo '       run sudo su -c "sudo -u apache /opt/invenio/bin/bibsched"'
echo '       wait for the UI to show up, then press A (switch to auto), wait, press Q (quit)'
echo '    Restart'
