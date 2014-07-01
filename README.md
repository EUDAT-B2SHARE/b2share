invenio-scripts
===============

Utility scripts for B2SHARE - Invenio:

- **Vagrantfile** is a vagrant configuration for a suitable development machine.

- **start-invenio-daemons.sh** will start the invenio daemons necessary for data ingestion and other background jobs


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

4. if needed: ON THE GUEST VM: If you want to restart the server and run it again:
   ```
   $ source ~/.bashrc
   $ workon b2share
   # make sure celeryd is running, see end of 'install_b2share.sh'
   $ inveniomanage runserver -d -r
   ```


    
### License

B2SHARE is licensed under the [GPL v3 license.](http://www.gnu.org/licenses/gpl-3.0.txt)
