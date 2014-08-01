echo; echo "=+=+= Provisioning VM for DEVELOPMENT =+=+="

cd /home/vagrant/
sudo /vagrant/provision_system.sh 2>&1 | tee provision.log
sudo chown -R vagrant: /home/vagrant
sudo su vagrant -c "/vagrant/install_b2share_dev.sh 2>&1 | tee install.log"
