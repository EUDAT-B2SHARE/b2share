echo; echo "=+=+= Provisioning VM for DEVELOPMENT7 =+=+="

cd /home/vagrant/
sudo /vagrant/provision_system7.sh 2>&1 | tee provision.log
sudo chown -R vagrant: /home/vagrant
sudo su vagrant -c "/vagrant/install_b2share.sh development 2>&1 | tee install.log"
