invenio-scripts
===============

Utility scripts for installing B2SHARE & Invenio:

## Installation Guide

Below is a guide for a full installation of Invenio on a CentOS VM via Vagrant (with Virtualbox).

Use guide Deployment (1.) for installing the latest version of `b2share-next`, and Development (2.) for development purposes. Deployment will clone the latest version of `b2share-next`, whereas Development will share the B2SHARE repository on your local machine (which can be a cloned fork).

*NOTE: only one VM can be active at the same time due to portforwarding!*


### Install Local Machine Dependencies

Download and install the following packages listed below for your operating system:

*NOTE: most Linux and OSX systems already have git installed. Windows users please use this guide: [`http://www.enrise.com/2012/12/git-and-vagrant-in-a-windows-environment/`](http://www.enrise.com/2012/12/git-and-vagrant-in-a-windows-environment/)*

1. VirtualBox: [`https://www.virtualbox.org/wiki/Downloads`](https://www.virtualbox.org/wiki/Downloads)
2. Vagrant: [`http://www.vagrantup.com/downloads.html`](http://www.vagrantup.com/downloads.html)
3. Git: [`http://git-scm.com/downloads`](http://git-scm.com/downloads) or [`http://git-scm.com/downloads/guis`](http://git-scm.com/downloads/guis)

### Changelog

1. `vagrant (up/ ssh/ halt etc.)` is surpassed by `vagrant (up/ ssh/ halt) default`, Vagrant is expanded with a development environment requiring alternate calling the default (old VM) setup;

2. `Vagrantfile` deployment (default) and development (dev) VM's split into two separate instances.


### 1. Deployment of latest version

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
   $ vagrant up default
   # access the VM via SSH
   $ vagrant ssh default
   ```

3. ON THE GUEST VM: Run `start_b2share.sh`, which will start the b2share server in development mode. You can now go on the host machine to `http://localhost:4000` and the b2share/invenio site should show up.
   ```bash
   # load virtual environment b2share
   $ workon b2share
   # start the b2share service
   $ /vagrant/start_b2share.sh
   ```

4. ON THE HOST: Open a browser and goto URL [`http://localhost:4000`](http://localhost:4000).


#### 1.1 Update Repository

This procedure will update B2SHARE with the latest version from github. All changes to local files will be overwritten!

*NOTE: `inveniomanage runserver` will detect changes in files, and restart the service accordingly*

```bash
$ vagrant ssh default
$ workon b2share
$ cd $WORKON_HOME/b2share/src/b2share
$ git pull
# or force reload (on local changes)
# DANGER: THIS WILL RESET ALL YOUR LOCAL CHANGES!
$ git fetch --all
$ git reset --hard origin/b2share-next
```


### 2. Development

On your host machine, create a clean folder and copy into it the whole content of `invenio-scripts/install`. Or clone `invenio-scripts` from github. Change working directory to this folder (`cd...`).

Moreover, on your host machine, create a clean folder and copy (or clone from github) into the path relative to `invenio-scripts/install/../../`.

*NOTE: Typically a HOST OS is the current machine you're using, which runs VirtualBox with Vagrant to run a GUEST OS, which is the VM.*

1. ON THE HOST: Clone git repository and goto the directory containing the Vagrantfile.
   ```bash
   cd /path/to/your/development-repos/
   # clone the invenio-scripts repository to your local machine
   $ git clone -b b2share-next https://github.com/EUDAT-B2SHARE/invenio-scripts
   # clone the b2share repository to your local machine (we recommend cloning your own fork of b2share!)
   $ git clone -b b2share-next https://github.com/EUDAT-B2SHARE/b2share
   $ cd invenio-scripts/install
   ```

2. ON THE HOST: Run `vagrant up` in the folder created above, and then (afte r the provisioning is completed) login into the newly created machine.
   ```bash
   # create the VM and provision it with B2Share and Invenio
   #  NOTE: this will take some time
   $ vagrant up dev
   # access the VM via SSH
   $ vagrant ssh dev
   ```

3. ON THE GUEST VM: Run `start_b2share.sh`, which will start the b2share server in development mode. You can now go on the host machine to `http://localhost:4000` and the b2share/invenio site should show up.
   ```bash
   # load virtual environment b2share
   $ workon b2share
   # start the b2share service
   $ /vagrant/start_b2share.sh
   ```
4. ON THE HOST: Open a browser and goto URL [`http://localhost:4000`](http://localhost:4000).

**Post-installation**

After the installation the b2share sources are located in `$WORKON_HOME/b2share/src/b2share`, and are shared between your HOST machine. Resulting in a changeable local repository. You have full control over the files in your local repository and can commit changes directly via git.

*NOTE: `inveniomanage runserver` will detect changes in files, and restart the service accordingly*



## Contributing

1. Fork `EUDAT-B2SHARE/invenio-scripts`;
2. Create a new branch (for `b2share-next`) on your fork;
3. Commit changes to your branch on your fork;
4. Publish your local branch;
5. Create a pull-request on `EUDAT-B2SHARE/invenio-scripts` branch: `b2share-next`

### Syncing Fork

After a pull-request you have to merge/ fast forward your fork with the latest commits from the master repository: `EUDAT-B2SHARE/invenio-scripts`

**Github has documentation on it:**

1. https://help.github.com/articles/configuring-a-remote-for-a-fork
2. https://help.github.com/articles/syncing-a-fork

**EUDAT-B2SHARE application:**

```bash
$ cd /path/to/your/fork/invenio-scripts
# add `EUDAT-B2SHARE/invenio-scripts` repository upstream
$ git add remote upstream https://github.com/EUDAT-B2SHARE/invenio-scripts.git
# verify remote upstream
$ git remote -v
# fetch upstream
$ git fetch upstream
# make sure you're on the `b2share-next` branch
$ git checkout b2share-next
# merge upstream branch
$ git merge upstream/b2share-next
```


## Files

- **Vagrantfile** is a vagrant configuration for a suitable development machine. Should be used with vagrant to create and start a virtual machine.

- **provision_system.sh** will install the necessary packages, python version and other dependencies needed by invenio. Called on VM provisioning.

- **install_b2share.sh** will install b2share (the b2share-next branch) and create the necessary configuration settings. Called on VM provisioning.

- **install_b2share_dev.sh** will install b2share from a local B2SHARE repository. It will create the necessary configuration settings. Called on VM dev provisioning.

- **start_b2share.sh** will start b2share with the required prerequisites. Must be called by the user via SSH.

- **\_collections.sql** is a sql script that creates the needed b2share collections (metadata domains). It is automatically called by the `install_b2share.sh` script.

- **\_install_python2.7.sh** will install python 2.7. It is automatically called by the `provision_system.sh` script.


## License

B2SHARE is licensed under the [GPL v3 license.](http://www.gnu.org/licenses/gpl-3.0.txt)
