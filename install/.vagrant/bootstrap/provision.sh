echo; echo "=+=+= Provisioning VM =+=+="

cd /home/vagrant/
sudo /vagrant/provision_system.sh 2>&1 | tee provision.log
sudo su vagrant -c "/vagrant/install_b2share.sh 2>&1 | tee install.log"
