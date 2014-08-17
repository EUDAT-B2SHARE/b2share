B2SHARE
=======

[![Build Status](https://travis-ci.org/EUDAT-B2SHARE/b2share.svg?branch=master)](https://travis-ci.org/EUDAT-B2SHARE/b2share)

B2SHARE is an user-friendly, secure, robust, reliable, and trusted service to share and store your **research data**. B2SHARE is able to add value to your research data via (domain tailored) metadata, and assigning Persistent Identifiers [PIDs](http://www.pidconsortium.eu/) to ensure long-lasting access and references. B2SHARE is one of the B2 services developed via [EUDAT](http://www.eudat.eu/).

**Deposit and release your data** via the generic interface, or select a community extension including domain-specific metadata fields. **Share your data** with others in a safe and trusted environment. **Scientific communities** are able to brand templates, and use their own collections with specific metadata.

B2SHARE is based on [Invenio](http://invenio-software.org/). Invenio enables you to run your own electronic preprint server, your own online library catalogue or a digital document system on the web. It complies with the Open Archive Initiative metadata harvesting protocol and uses [MARC21](http://www.loc.gov/marc/) as its underlying bibliographic standard.

**Demo site:** https://b2share.eudat.eu/

## Development Installation

Installing B2SHARE requires an installation of Invenio first, than the deployment of the B2SHARE module with some overlays. These steps are covered in the [README.md](https://github.com/EUDAT-B2SHARE/invenio-scripts/blob/master/README.md), in the [`EUDAT-B2SHARE/invenio-scripts`](https://github.com/EUDAT-B2SHARE/invenio-scripts/tree/master) repository.

*NOTE: Vagrant is a tool that manages VMs in numerous providers (like VirtualBox). VirtualBox through Vagrant is free to use (and only supported by B2SHARE). Vagrant provides preinstalled VMs called boxes through: [Vagrantbox.es](http://www.vagrantbox.es/). Everyone is able to commit their boxes, however due to the setup we urge you NOT TO USE a Vagrantbox in production, ever!*

**Follow the installation guide:** [README.md](https://github.com/EUDAT-B2SHARE/invenio-scripts/blob/master/README.md)


## Contributing

1. Fork `EUDAT-B2SHARE/b2share`;
2. Create a new branch (for `master`) on your fork;
3. Commit changes to your branch on your fork;
4. Publish your local branch;
5. Create a pull-request on `EUDAT-B2SHARE/b2share` branch: `master`

## Syncing Fork

After a pull-request you have to merge/ fast forward your fork with the latest commits from the master repository: `EUDAT-B2SHARE/b2share`

**Github has documentation on it:**

1. https://help.github.com/articles/configuring-a-remote-for-a-fork
2. https://help.github.com/articles/syncing-a-fork

**EUDAT-B2SHARE application:**

```bash
$ cd /path/to/your/fork/b2share
# add `EUDAT-B2SHARE/b2share` repository upstream
$ git add remote upstream https://github.com/EUDAT-B2SHARE/b2share.git
# verify remote upstream
$ git remote -v
# fetch upstream
$ git fetch upstream
# make sure you're on the `master` branch
$ git checkout master
# merge upstream branch
$ git merge upstream/master
```

## Testing

* stub
