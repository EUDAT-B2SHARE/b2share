#!/bin/bash

# # invoke with
# sudo /vagrant/provision_system.sh 2>&1 | tee provision.log

MYSQL_ROOT=invenio
USER=vagrant

if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root"
   exit 1
fi

echo; echo "### Stop iptables"
/etc/init.d/iptables stop
chkconfig iptables off

echo; echo "### System update"
yum -y update

echo; echo "### Install wget vim epel"
yum install -y wget vim epel-release

echo; echo "### Install lots of packages"
yum install -y screen strace openssl-devel \
           mysql mysql-devel sqlite-devel MySQL-python \
           python-pip python-chardet python-simplejson \
           pylint pyflakes python-BeautifulSoup python-devel \
           libxml2-devel libxml2-python libxslt-devel libxslt-python python-magic \
           gcc automake autoconf git gnuplot \
           redis python-redis \
           unzip bzip2-devel bzip2 xz-libs \
           java-1.7.0-openjdk-devel npm html2text netpbm giflib-devel \
           poppler ghostscript-devel gettext-devel \
           python-virtualenv python-virtualenvwrapper

echo; echo "### Install mysql server"
rpm -Uvh http://dev.mysql.com/get/mysql-community-release-el7-5.noarch.rpm
yum install -y mysql-server

echo; echo "### Groupinstall development"
yum groupinstall -y development

echo; echo "### Install grunt & bower"
npm install -g grunt grunt-cli bower

echo; echo "### Start redis"
chkconfig redis on
service redis start

echo; echo "### Start mysql"
chkconfig mysqld on
service mysqld start
mysqladmin -u root password $MYSQL_ROOT
