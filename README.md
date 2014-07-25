invenio-scripts
===============

Utility scripts for installing B2SHARE & Invenio:

## Development Installation

Below is a guide for a full installation of Invenio on a CentOS VM via Vagrant (with Virtualbox).


### Install development dependencies

Download and install the following packages listed below for your operating system:

*NOTE: most Linux and OSX systems already have git installed. Windows users please use this guide: `http://www.enrise.com/2012/12/git-and-vagrant-in-a-windows-environment/`*

1. VirtualBox: `https://www.virtualbox.org/wiki/Downloads`
2. Vagrant: `http://www.vagrantup.com/downloads.html`
3. Git: `http://git-scm.com/downloads` or `http://git-scm.com/downloads/guis`


### Running installation scripts

On your host machine, create a clean folder and copy into it the whole content of `invenio-scripts/install`. Or clone `invenio-scripts` from github. Change working directory to this folder (`cd...`)

*NOTE: Typically a HOST OS is the current machine you're using, which runs VirtualBox with Vagrant to run a GUEST OS, which is the VM.*

1. ON THE HOST: Clone git repository and goto the directory containing the Vagrantfile.
   ```bash
   # clone the git repository to your local machine
   $ git clone -b b2share-next https://github.com/EUDAT-B2SHARE/invenio-scripts
   $ cd invenio-scripts/install
   ```

2. ON THE HOST: Run `vagrant up` in the folder created above, and then (afte r the provisioning is completed) login into the newly created machine.
   ```bash
   # create the VM and provision it with B2Share and Invenio
   #  NOTE: this will take some time
   $ vagrant up
   # access the VM via SSH
   $ vagrant ssh
   ```

3. ON THE GUEST VM: Run `start_b2share.sh`, which will start the b2share server in development mode. You can now go on the host machine to `http://localhost:4000` and the b2share/invenio site should show up.
   ```bash
   # load virtual environment b2share
   $ workon b2share
   # start the b2share service
   $ /vagrant/start_b2share.sh
   ```

4. ON THE HOST: Open a browser and goto URL [`http://localhost:4000`](http://localhost:4000).


### Development

After the installation the b2share sources are located in `$WORKON_HOME/b2share/src/b2share`. Use the following commands to go to that folder:
```bash
$ vagrant ssh
$ workon b2share
$ cdvirtualenv
$ cd src/b2share
```

##### Pushing changes to git

* stub


### Files

- **Vagrantfile** is a vagrant configuration for a suitable development machine. Should be used with vagrant to create and start a virtual machine.

- **provision_system.sh** will install the necessary packages, python version and other dependencies needed by invenio. Must be called by the user.

- **install_b2share.sh** will install b2share (the b2share-next branch) and create the necessary configuration settings. Must be called by the user.

- **start_b2share.sh** will start b2share with the required prerequisites. Must be called by the user.

- **\_collections.sql** is a sql script that creates the needed b2share collections (metadata domains). It is automatically called by the `install_b2share.sh` script.

- **\_install_python2.7.sh** will install python 2.7. It is automatically called by the `provision_system.sh` script.


### License

B2SHARE is licensed under the [GPL v3 license.](http://www.gnu.org/licenses/gpl-3.0.txt)
