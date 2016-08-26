B2Share installation
====================

1. Install B2SHARE for evaluation, using Docker
-----------------------------------------------

1.0 Prerequisite: clone B2SHARE
--------------------------------

Current installation process requires a local clone of B2SHARE.

.. code-block:: console

    $ git clone git@github.com:EUDAT-B2SHARE/b2share.git

1.1 Prerequisite: B2ACCESS configuration
----------------------------------------

B2SHARE requires B2ACCESS for user management. For this purpose you must create
a new B2ACCESS OAuth client, providing as the 'return URL' the address of the
local B2SHARE server and the authorization path:
https://$FQDN/api/oauth/authorized/b2access/ (where $FQDN must be replaced with
the domain of the B2SHARE server). After successfully registering the
B2ACCESS account please set the following environment variables with the
username and password provided for the B2ACCESS account:

.. code-block:: console

    $ export B2ACCESS_CONSUMER_KEY=...    # the username used for registration
    $ export B2ACCESS_SECRET_KEY=...      # the password used for registration

Additional customizations of the B2ACCESS server configuration can be performed
after B2SHARE is provisioned (after the b2share.sh script runs
``/usr/bin/b2share demo load_config``). The script creates a configuration file
in ``/usr/var/b2share-instance/b2share.cfg``, which can be edited as necessary.


1.2. Run a B2Share demo with Docker
-----------------------------------

If you can run docker on the same host (on Linux or with Docker for
Mac/Windows), go into the ``dockerize`` folder and then run ``docker-compose``:

.. code-block:: console

    $ cd b2share/dockerize
    $ export B2ACCESS_CONSUMER_KEY=...    # the username used for registration
    $ export B2ACCESS_SECRET_KEY=...      # the password used for registration
    $ export B2SHARE_JSONSCHEMAS_HOST='<FQDN>'
    $ # Where <FQDN> is the domain of the B2SHARE server
    $ export LOAD_DEMO_CONFIG=1
    $ docker-compose up

After the docker image is built and running, B2SHARE will be available at
https://<YOUR DOCKER SERVER>

2. Install B2SHARE for development
----------------------------------

Before installing B2Share you will need the following software:

- ``python3``
- ``virtualenv`` and ``virtualenvwrapper``

.. code-block:: console

    $ # on OSX, with brew:
    $ brew install python --framework --universal
    $ pip install virtualenv virtualenvwrapper

- ``docker``, ``docker-compose``, and ``docker-machine``

If the conditions are satisfied, open one terminal window and download in a
temporary folder the ``devenv/docker-compose`` and ``devenv/run_demo.sh``
files:

.. code-block:: console

    $ mdir develop-b2share
    $ cd develop-b2share
    $ curl -O https://raw.githubusercontent.com/EUDAT-B2SHARE/b2share/evolution/devenv/docker-compose.yml
    $ curl -O https://raw.githubusercontent.com/EUDAT-B2SHARE/b2share/evolution/devenv/run_demo.sh


Then start the ``run_demo.sh`` script:

.. code-block:: console

    $ chmod +x ./run_demo.sh
    $ ./run_demo.sh

The script will create a python virtualenv, clone the evolution branch of
B2SHARE into it, install the necessary python packages, build the web UI and
start the Flask server in development mode. B2SHARE should be available at
http://localhost:5000.

If working on the web UI, see also: https://github.com/EUDAT-B2SHARE/b2share/wiki/Developer's-corner.
