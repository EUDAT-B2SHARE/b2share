#!/bin/bash

# # use this on your HOST machine, not the VM
# # it uses vagrant to install B2SHARE for development

vagrant up default
vagrant ssh-config > .sshconfig
vagrant rsync
ssh -F .sshconfig vagrant@default '/vagrant/install_b2share.sh development'
