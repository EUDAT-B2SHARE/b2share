B2Share installation
====================

1. Install B2SHARE for evaluation, using Docker
-----------------------------------------------

1.1. If running Docker locally
------------------------------

If you can run docker on the same host (on Linux), go into the ``dockerize`` folder:

.. code-block:: console

    $ git clone git@github.com:EUDAT-B2SHARE/b2share.git --branch evolution
    $ cd b2share/dockerize

and then run ``docker-compose`` as below:

.. code-block:: console

    $ export B2SHARE_SERVER_NAME=localhost
    $ docker-compose up

After the docker image is built and running, b2share will be available at http://localhost:5000

Logging in with B2ACCESS requires some configuration; please check for more details in the B2ACCESS configuration section below.


1.2. If running Docker with docker-machine and virtualbox
---------------------------------------------------------

If you can not run docker on the same host but you can use docker-machine and a virtualbox VM (e.g. on OSX), go into the ``dockerize`` folder:

.. code-block:: console

    $ git clone git@github.com:EUDAT-B2SHARE/b2share.git --branch evolution
    $ cd b2share/dockerize

and then run the following script:

.. code-block:: console

    $ ./run_docker.sh

The script will try to create a new VM box using docker-machine and virtualbox, and run docker-compose on it.
After the docker image is built and started, a message will be displayed pointing the URL of the B2SHARE instance.

Logging in with B2ACCESS requires some configuration; please check for more details in the B2ACCESS configuration section below.

1.3 B2ACCESS configuration
----------------------------

In order for the users to be able to login using B2ACCESS, an additional configuration step must be performed. The local administrator must create a new
OAuth client account at https://unity.eudat-aai.fz-juelich.de:8443/home/home, providing as the return URL the address of the local B2SHARE server
and the authorization path (e.g. http://localhost:5000/api/oauth/authorized/b2access/ for a localhost installation, or
http://$(docker ip b2sharebeta):5000/api/oauth/authorized/b2access/ for an installation using with docker-machine). After successfully
registering the B2ACCESS account, the administrator must set the following environment variables with the username and password provided
for the B2ACCESS account, before starting the service by running ``docker-compose`` or the ``run_docker.sh`` script:

.. code-block:: console

    $ export B2ACCESS_CONSUMER_KEY=...
    $ export B2ACCESS_SECRET_KEY=...
    $ docker-compose up # or ./run_docker.sh

Additional customizations of the B2ACCESS server configuration can be performed after the b2share is provisioned (after the b2share.sh script
runs ``/usr/bin/b2share demo load_config``). The script creates a configuration file in ``/usr/var/b2share-instance/b2share.cfg``, which can be
edited as necessary.


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
