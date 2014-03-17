invenio-scripts
===============

Utility scripts for Invenio:

- **Vagrantfile** is a vagrant configuration for a suitable development machine. You need to provision it manually with the **install-everything-from-scratch-rh.sh** script, after it boots

- **install-b2share-from-scratch-rh.sh** will use the other scripts to install and configure a fresh machine

- **install-invenio-deps-rh.sh** will install the OS required packages for invenio

- **wipe-and-install-invenio-rh.sh** will WIPE (if existing) and reinstall the invenio base system. This will not install b2share, for that you need to run deployment scripts in the b2share repository.

- **start-daemons-rh.sh** will start the invenio daemons necessary for data ingestion and other background jobs

- **invenio-local.conf** contains additional invenio configurations, specific for b2share. It is not a script but a configuration file.

The scripts above are designed to run on a RedHat/CentOS machine. The remaining scripts target ubuntu/debian machines.

    
### License

B2SHARE is licensed under the [GPL v3 license.](http://www.gnu.org/licenses/gpl-3.0.txt)
