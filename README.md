invenio-scripts
===============

Utility scripts for B2SHARE - Invenio:

### Installation

On your host machine, create a clean folder and copy into it the whole content of `invenio-scripts/install`. Change working directory to this folder (`cd...`)

1. ON THE HOST: Run `vagrant up` in the folder created above and then login into the newly created machine:
   ```
   $ vagrant up
   $ vagrant ssh
   ```

2. ON THE GUEST VM: Run `provision_system.sh`, which will install the needed packages, python 2.7, other python tools, grunt and bower
   ```
   $ sudo /vagrant/provision_system.sh 2>&1 | tee provision.log
   ```

3. ON THE GUEST VM: Run `install_b2share.sh`, which will clone and install the b2share-next branch. The script should never stop: at the very end it will start the invenio server in development mode (interactive mode)
   ```
   $ /vagrant/install_b2share.sh 2>&1 | tee install.log
   ```

   You can now go on the host machine to `http://localhost:4000` and the  b2share/invenio site should show up.

If you need to stop the server you can restart b2share with the `inveniomanage runserver -d -r` command, as described below.

### Other

- If you want to restart the server and run it again:
   ```
   $ source ~/.bashrc
   $ workon b2share
   # make sure celeryd is running, see end of 'install_b2share.sh'
   $ inveniomanage runserver -d -r
   ```

### Files

- **Vagrantfile** is a vagrant configuration for a suitable development machine. Should be used with vagrant to create and start a virtual machine.

- **provision_system.sh** will install the necessary packages, python version and other dependencies needed by invenio. Must be called by the user.

- **install_b2share.sh** will install b2share (the b2share-next branch) and create the necessary configuration settings. Must be called by the user.

- **start-invenio-daemons.sh** will start the invenio daemons necessary for data ingestion and other background jobs. It is automatically run by the `install_b2share.sh` script.

- **collections.sql** is a sql script that creates the needed b2share collections. It is automatically called by the `install_b2share.sh` script.

- **\_install_python2.7.sh** will install python 2.7. It is automatically called by the `provision_system` script.

    
### License

B2SHARE is licensed under the [GPL v3 license.](http://www.gnu.org/licenses/gpl-3.0.txt)
