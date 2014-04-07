EUDAT B2SHARE
=================

Content:
 * b2share - code specific to B2SHARE in form of the Invenio overlay
 * invenio - modifications to the Invenio core files
 * deployment - deployment support scripts

### Installing B2SHARE
 
Find a new Centos/RedHat VM and install the base invenio system and then the b2share overlay. Use the B2SHARE/invenio-scripts repository for this (the `Vagrantfile` and `install-b2share-from-scratch-rh.sh`) 
   - 1.1. Create a new folder
   - 1.2. Get into this directory and download manually the `Vagrantfile` and `install-b2share-from-scratch-rh.sh`
   - 1.3. Go to a terminal into this directory and run `vagrant up`
   - 1.4. Run `vagrant ssh` to connect to the VM, then `cd /vagrant` and `sudo ./install-b2share-from-scratch.sh`. The install can take ~2 hours.

You now should be able to connect to your machine (not the VM) at `https://localhost:4443` and see the b2share site (with no deposits)

### Developer tools
 1. Add the following configuration variables to invenio-local.conf: `CFG_DEVEL_SITE = 1` and `CFG_DEVEL_TOOLS = werkzeug-debugger` then rebuild the python config file with `sudo -u apache /opt/invenio/bin/inveniocfg --update-config-py`
 2. Either remove the redis cache, see the last actions in `install-b2share-from-scratch-rh.sh` script (but then some search functions will no longer work) or remember to delete the cache whenever something changes (with `redis-cli flushall`)
 
### Development workflow

 If you have used the Vagrant environment, you can directly work in the folder created previously. The `install-b2share-from-scratch-rh.sh` script creates git repositories in this folder. Vagrant shares the folder between the host and the VM, so all changes in the git repositories from the host are mirrored to the VM. When done editing code, switch to the VM, go to `/vagrant/b2share` and run `./deployment/deploy_overlay-rh.sh`, then switch back to the host browser, reload the `https://localhost:4443/` webpage and test your changes.

    
### License

B2SHARE is licensed under the [GPL v3 license.](http://www.gnu.org/licenses/gpl-3.0.txt)

