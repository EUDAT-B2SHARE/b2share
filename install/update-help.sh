#!/bin/bash 

INVENIO_DIR=/opt/invenio

git config --global http.sslVerify false
cd simplestore.wiki
git pull

cp B2SHARE-About.md $INVENIO_DIR/etc/templates/b2share-about.markdown
cp B2SHARE-FAQ.md $INVENIO_DIR/etc/templates/b2share-faq.markdown
cp B2SHARE-TOU.md $INVENIO_DIR/etc/templates/b2share-tou.markdown
cp User-Documentation.md $INVENIO_DIR/etc/templates/b2share-guide.markdown

cp -rf img/* /opt/invenio/var/img/

