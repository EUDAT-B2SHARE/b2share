EUDAT B2SHARE
=================

Content:
 * b2share - code specific to B2SHARE in form of the Invenio overlay
 * invenio - modifications to the Invenio core files
 * deployment - deployment support scripts

### First steps with B2SHARE development:
 1. Find a new Centos/RedHat VM and install the base invenio system and then the b2share overlay. Use the B2SHARE/invenio-scripts repository for this (the Vagrantfile and install-b2share-from-scratch.sh) 
   - 1.1. Create a new directory
   - 1.2. Get into this directory and download manually the Vagrantfile and install-b2share-from-scratch.sh
   - 1.3. Go to a terminal into this directory and run 'vagrant up'
   - 1.4. Run 'vagrant ssh' to connect to the VM, then 'cd /vagrant' and 'sudo ./install-b2share-from-scratch.sh'
   - 1.5. (Wait for 2 hours)
 2. Be sure to remove the redis cache, see the last actions in install-b2share-from-scratch.sh script
 3. You should now be able to connect to your machine (not the VM) at https://localhost:4443 and see the b2share site (with no deposits)
 4. If you have used the Vagrant environment, you can directly work on the git code on your machine. When done editing code, switch to the VM, go to /vagrant/b2share and run ./deployment/deploy_overlay-rh.sh, then reload the webpage and test your change
