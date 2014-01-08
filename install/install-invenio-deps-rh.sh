#!/bin/bash 
#run as root

MYSQLPASS='invenio'

wget http://www.mirrorservice.org/sites/dl.fedoraproject.org/pub/epel/6/i386/epel-release-6-8.noarch.rpm
rpm -Uvh epel-release-6-8.noarch.rpm
yum install -y git python-pip httpd mysql mysql-server gnuplot html2text netpbm \
               python-chardet python-simplejson mod_wsgi mod_ssl MySQL-python \
               libxml2-python libxslt-python poppler ghostscript-devel \
               giflib-devel sbcl pylint pychecker pyflakes epydoc mod_xsendfile \
               python-BeautifulSoup automake16 gcc python-devel mysql-devel \
               libxslt-devel libxml2-devel gettext-devel python-magic \
               java-1.7.0-openjdk-devel redis python-redis\
               automake autoconf unzip

#redis
/sbin/service redis start
/sbin/chkconfig redis on

#apache
/sbin/service httpd start
/sbin/chkconfig httpd on

echo "Include /opt/invenio/etc/apache/invenio-apache-vhost.conf
Include /opt/invenio/etc/apache/invenio-apache-vhost-ssl.conf
TraceEnable off
SSLProtocol all -SSLv2" >> /etc/httpd/conf/httpd.conf

chgrp apache /opt
chmod g+w /opt
mkdir -p /opt/invenio/lib/python/invenio
ln -s /opt/invenio/lib/python/invenio /usr/lib/python2.6/site-packages/invenio

#mysql 
#better to run mysql_secure_installation
/sbin/service mysqld start
chkconfig mysqld on
/usr/bin/mysqladmin -u root password $MYSQLPASS
/usr/bin/mysqladmin -u root --password=$MYSQLPASS -h localhost.localdomain password $MYSQLPASS

git config --global http.sslVerify false
git clone -v -b next https://github.com/SimpleStore/invenio.git

cd invenio
git fetch # just in case, to get then new tags
git checkout tags/b2share-v2 -b bshare-v2

python-pip install --upgrade distribute
python-pip install -r requirements.txt
python-pip install -r requirements-flask.txt
python-pip install -r requirements-extras.txt
python-pip install -r requirements-flask-ext.txt

#seems to be missed or old
python-pip install --upgrade redis
python-pip install babel
