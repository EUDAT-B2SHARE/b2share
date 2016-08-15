B2Share installation
====================

1. Install B2SHARE for evaluation, using Docker
-----------------------------------------------

1.0 Prerequisite: FQDN for nginx
--------------------------------

B2SHARE runs in a python environment, proxied by default by nginx. Before running B2SHARE a nginx configuration file must be created. The ``create_nginx_conf.sh`` script, located in the ``dockerize`` folder, can be used for this purpose.

.. code-block:: console

    $ git clone git@github.com:EUDAT-B2SHARE/b2share.git
    $ cd b2share/dockerize
    $ ./create_nginx_conf.sh

The ``create_nginx_conf.sh`` script will ask for the FQDN (Fully Qualified Domain Name) of the local server. If you are only trying to test B2SHARE, you can use a local domain, e.g. 'b2share2.local'. In this case please add the FQDN value to your hosts file to connect it with the real IP, e.g.: ``192.168.99.100  b2share2.localhost`` if using docker-machine or ``127.0.0.1  b2share2.localhost`` if running Docker locally.


1.1 Prerequisite: B2ACCESS configuration
----------------------------------------

B2SHARE requires B2ACCESS for user management. For this purpose you must create a new B2ACCESS OAuth client, providing as the 'return URL' the address of the local B2SHARE server and the authorization path: https://$FQDN/api/oauth/authorized/b2access/ (where $FQDN must be replaced with the domain name described above). After successfully registering the B2ACCESS account please set the following environment variables with the username and password provided for the B2ACCESS account:

.. code-block:: console

    $ export B2ACCESS_CONSUMER_KEY=...    # the username used for registration
    $ export B2ACCESS_SECRET_KEY=...      # the password used for registration

Additional customizations of the B2ACCESS server configuration can be performed after B2SHARE is provisioned (after the b2share.sh script runs ``/usr/bin/b2share demo load_config``). The script creates a configuration file in ``/usr/var/b2share-instance/b2share.cfg``, which can be edited as necessary.


1.2. If running Docker locally
------------------------------

If you can run docker on the same host (on Linux or with Docker for Mac/Windows), go into the ``dockerize`` folder, define the B2SHARE_SERVER_NAME variable to point to the FQDN (see above), define the B2ACCESS application key and secret (see above), and then run ``docker-compose``:

.. code-block:: console

    $ cd b2share/dockerize
    $ export B2SHARE_SERVER_NAME=b2share2.localhost
    $ export B2ACCESS_CONSUMER_KEY=...    # the username used for registration
    $ export B2ACCESS_SECRET_KEY=...      # the password used for registration
    $ docker-compose up

After the docker image is built and running, b2share will be available at https://$B2SHARE_SERVER_NAME


1.3. If running Docker with docker-machine and virtualbox
---------------------------------------------------------

If you can not run docker on the same host but you can use docker-machine and a virtualbox VM, go into the ``dockerize`` folder and then run the `run_docker` script:

.. code-block:: console

    $ cd b2share/dockerize
    $ export B2SHARE_SERVER_NAME=b2share2.localhost
    $ export B2ACCESS_CONSUMER_KEY=...    # the username used for registration
    $ export B2ACCESS_SECRET_KEY=...      # the password used for registration
    $ ./run_docker.sh

The script will try to create a new VM box using docker-machine and virtualbox, and run docker-compose on it.
After the docker image is built and running, b2share will be available at https://$B2SHARE_SERVER_NAME



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

If the conditions are satisfied, open one terminal window and download in a temporary folder the ``devenv/docker-compose`` and ``devenv/run_demo.sh`` files:

.. code-block:: console

    $ mdir develop-b2share
    $ cd develop-b2share
    $ curl -O https://raw.githubusercontent.com/EUDAT-B2SHARE/b2share/evolution/devenv/docker-compose.yml
    $ curl -O https://raw.githubusercontent.com/EUDAT-B2SHARE/b2share/evolution/devenv/run_demo.sh


Then start the ``run_demo.sh`` script:

.. code-block:: console

    $ chmod +x ./run_demo.sh
    $ ./run_demo.sh

The script will create a python virtualenv, clone the evolution branch of B2SHARE into it, install the necessary python packages, build the web UI and start the Flask server in development mode. B2SHARE should be available at http://localhost:5000.

If working on the web UI, see also: https://github.com/EUDAT-B2SHARE/b2share/wiki/Developer's-corner.
