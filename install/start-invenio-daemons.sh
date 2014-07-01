#!/bin/bash

USER=vagrant # 'vagrant' for development and 'apache' for production
PYPATH=/opt/python-2.7.6

source $PYPATH/bin/virtualenvwrapper.sh 

workon b2share
if [ $? -ne 0 ]; then
    echo "'workon b2share' failed"
    exit 1
fi

cdvirtualenv
if [ $? -ne 0 ]; then
    echo "'cdvirtualenv' failed"
    exit 1
fi

# double sudo to bypass some errors
sudo sudo -u $USER ./bin/bibindex -f50000 -s5m -uadmin
sudo sudo -u $USER ./bin/bibreformat -oHB -s5m -uadmin
sudo sudo -u $USER ./bin/webcoll -v0 -s5m -uadmin
sudo sudo -u $USER ./bin/bibrank -f50000 -s5m -uadmin
sudo sudo -u $USER ./bin/bibsort -s5m -uadmin
