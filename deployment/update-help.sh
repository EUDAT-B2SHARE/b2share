#!/bin/bash 

INVENIO_DIR=/opt/invenio

git config --global http.sslVerify false
cd ../b2share.wiki
git pull

cp -v B2SHARE-About.md $INVENIO_DIR/etc/templates/b2share-about.markdown
cp -v B2SHARE-FAQ.md $INVENIO_DIR/etc/templates/b2share-faq.markdown
cp -v B2SHARE-TOU.md $INVENIO_DIR/etc/templates/b2share-tou.markdown
cp -v User-Documentation.md $INVENIO_DIR/etc/templates/b2share-guide.markdown

cp -vrf img /opt/invenio/var/www/
