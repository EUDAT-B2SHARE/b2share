To install the b2share-pu branch:

1. Run `vagrant up` in this folder (where the README is located) and login into the machine:
   ```
   $ vagrant up
   $ vagrant ssh
   ```

2. Run `provision_system.sh`, which will install the needed packages, python 2.7, other python tools, grunt and bower
   ```
   $ sudo /vagrant/provision_system.sh 2>&1 | tee provision.log
   ```

3. Run `install_b2share.sh`, which will clone and install the b2share-pu branch. The script should never stop: at the very end it will start the invenio server in development mode (interactive mode)
   ```
   $ /vagrant/install_b2share.sh 2>&1 | tee install.log
   ```

   You can now go on the host machine to `http://localhost:4000` and the bare invenio site (future b2share) should show up.

4. If you want to restart the server and run it again:
   ```
   $ source ~/.bashrc
   $ workon b2share
   # make sure celeryd is running, see end of 'install_b2share.sh'
   $ inveniomanage runserver
   ```
