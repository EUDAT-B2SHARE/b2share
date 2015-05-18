B2SHARE
=======

[![Build Status](https://travis-ci.org/EUDAT-B2SHARE/b2share.svg?branch=master)](https://travis-ci.org/EUDAT-B2SHARE/b2share)

B2SHARE is an user-friendly, secure, robust, reliable, and trusted service to share and store your **research data**. B2SHARE is able to add value to your research data via (domain tailored) metadata, and assigning Persistent Identifiers [PIDs](http://www.pidconsortium.eu/) to ensure long-lasting access and references. B2SHARE is one of the B2 services developed via [EUDAT](http://www.eudat.eu/).

**Deposit and release your data** via the generic interface, or select a community extension including domain-specific metadata fields. **Share your data** with others in a safe and trusted environment. **Scientific communities** are able to brand templates, and use their own collections with specific metadata.

B2SHARE is based on [Invenio](http://invenio-software.org/). Invenio enables you to run your own electronic preprint server, your own online library catalogue or a digital document system on the web. It complies with the Open Archive Initiative metadata harvesting protocol and uses [MARC21](http://www.loc.gov/marc/) as its underlying bibliographic standard.

**Demo site:** https://b2share.eudat.eu/

## Development Installation

Installing B2SHARE via Vagrant is covered in the guide below. Please note B2SHARE depends on Invenio, which is contained within this repository as well.

*NOTE: it's no longer required to use `invenio-scripts` to install B2SHARE!*

Vagrant is a tool that manages VMs in numerous providers (like VirtualBox). VirtualBox through Vagrant is free to use (and only supported by B2SHARE). Vagrant provides preinstalled VMs called boxes through: [Vagrantbox.es](http://www.vagrantbox.es/). Everyone is able to commit their boxes, however due to the setup we urge you NOT TO USE a Vagrantbox in production, ever!

#### Prerequisites

Download and install the following packages, listed below, for your operating system.

* VirtualBox: https://www.virtualbox.org/wiki/Downloads
* Vagrant: http://www.vagrantup.com/downloads.html
* Git: http://git-scm.com/downloads or http://git-scm.com/downloads/guis

#### Installing from Git

*NOTE: Typically a HOST OS is the current machine you're using, which runs VirtualBox with Vagrant to run a GUEST OS, which is the VM.*

**1. ON THE HOST: Clone git repository and goto the directory containing the Vagrantfile.**

```bash
cd /path/to/your/development-repos/
git clone -b master git@github.com:EUDAT-B2SHARE/b2share.git
cd b2share/install
```

**2. ON THE HOST: Run `./install.sh` in the folder created above, and then (after the provisioning is completed) login into the newly created machine.**

```bash
# create the VM and provision B2SHARE automatically (this will take time)
./install.sh
# access the VM via SSH (logging into the guest)
vagrant ssh default
```

**3. ON THE GUEST VM: Run `start_b2share.sh`, which will start the b2share server in development mode. You can now go on the host machine to `http://localhost:4000` and the b2share/invenio site should show up.**

```bash
# load virtualenv
workon b2share
# start service
/vagrant/start_b2share.sh
```

**4. ON THE HOST: Open a browser and goto URL http://localhost:4000.**

## Contributing

We appreciate contributions to our repository. Before you fork and make pull-requests please visit our wiki: https://github.com/EUDAT-B2SHARE/b2share/wiki/Contributing

