To install the invenio/pu branch:

1. run vagrant up in this folder (where the README is located) and login into the machine:
$ vagrant up
$ vagrant ssh

2. Run `provision_system.sh`, which will install the needed packages, python 2.7 and other python tools
$ cd
$ sudo /vagrant/provision_system.sh 2>&1 | tee /vagrant/provision.log

3. Run `install_invenio.sh`, which will clone and install the invenio/pu branch
$ sudo PATH="/opt/python-2.7.6/bin:$PATH" /vagrant/install_invenio.sh 2>&1 | tee /vagrant/install.log

4. run the server in development mode:
$ PATH="/opt/python-2.7.6/bin:$PATH" inveniomanage runserver
