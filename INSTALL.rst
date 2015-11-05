B2Share installation
====================

1. IMPORTANT
------------

This installation workflow is only valid for the `evolution` branch in
development mode.

2. Prerequisites
----------------

Before installing B2Share you will need the following software:
- python
- python virtualenv
- docker

.. code-block:: console

    $ brew install python --framework --universal
    $ pip install virtualenv
    $ pip install virtualenvwrapper
    # edit the Bash profile
    $ $EDITOR ~/.bash_profile

Add the following to the file you have opened and paste the following lines.

.. code-block:: text

    export WORKON_HOME=~/.virtualenvs
    source /usr/local/bin/virtualenvwrapper.sh

The dev environment supposes that the docker machine is called b2share. If
you are on mac you can create it like this:

.. code-block:: console
    $ docker-machine create --driver virtualbox b2share


3. Development environment installation
---------------------------------------

Create a python virtual environment.

.. code-block:: console

    $ # choose an unique name for your virtual environment
    $ export VENAME=b2share-evolution
    $ mkvirtualenv $VENAME
    (b2share-evolution)$ # we are in the b2share-evolution environment now and
    (b2share-evolution)$ # can leave it using the deactivate command.
    (b2share-evolution)$ deactivate
    $ # Now join it back, recreating it would fail.
    $ workon b2share-evolution
    (b2share-evolution)$ # That's all there is to know about it.


Then clone the repository and install the python dependencies:

.. code-block:: console

    $ # Enable the virtual environment we previously created
    $ workon b2share-evolution
    (b2share-evolution)$ # Go to its working directory
    (b2share-evolution)$ cdvirtualenv
    (b2share-evolution)$ mkdir src && cd src
    (b2share-evolution)$ # let's clone the repositiory
    (b2share-evolution)$ git clone git@github.com:EUDAT-B2SHARE/b2share.git --branch evolution
    (b2share-evolution)$ cd b2share
    (b2share-evolution)$ # install b2share python dependencies.
    (b2share-evolution)$ pip install -r requirements.txt

Let's start docker containers with mysql, elasticsearch and redis

.. code-block:: console

    (b2share-evolution)$ # Go to b2share directory
    (b2share-evolution)$ cd $VIRTUAL_ENV/src/b2share/devenv
    (b2share-evolution)$ docker-compose up
    Starting devenv_elasticsearch_1...
    Starting devenv_redis_1...
    Recreating devenv_mysql_1...


Open another terminal, initialize b2share and start celery:

.. code-block:: console

    $ # Enable docker environment
    $ eval $(docker-machine env default)
    $ # Enable the virtual environment we previously created
    $ workon b2share-evolution
    (b2share-evolution)$ # Go to its working directory
    (b2share-evolution)$ cdvirtualenv src/b2share
    (b2share-evolution)$ # Set the env variables
    (b2share-evolution)$ source ./devenv/docker_env.sh
    (b2share-evolution)$ celery worker -E -A invenio_celery.celery --workdir=$VIRTUAL_ENV

     -------------- celery@pb-d-128-141-246-93.cern.ch v3.1.18 (Cipater)
    ---- **** -----
    --- * ***  * -- Darwin-14.5.0-x86_64-i386-64bit
    -- * - **** ---
    - ** ---------- [config]
    - ** ---------- .> app:         invenio:0x110296310 (invenio_celery.InvenioLoader)
    - ** ---------- .> transport:   redis://localhost:6379/1
    - ** ---------- .> results:     redis://localhost:6379/1
    - *** --- * --- .> concurrency: 4 (prefork)
    -- ******* ----
    --- ***** ----- [queues]
     -------------- .> celery           exchange=celery(direct) key=celery

Open another terminal and clone the AngularJS-UI

.. code-block:: console
    $ # Enable docker environment
    $ eval $(docker-machine env default)
    $ # Enable the virtual environment we previously created
    $ workon b2share-evolution
    (b2share-evolution)$ cd $VIRTUAL_ENV/src
    (b2share-evolution)$ git clone git@github.com:EUDAT-B2SHARE/ui-frontend.git
    (b2share-evolution)$ # Install it
    (b2share-evolution)$ cd ui-frontend
    (b2share-evolution)$ npm install
    (b2share-evolution)$ # export the path so that the files are served by
                         # the flask application
    (b2share-evolution)$ export B2SHARE_UI_PATH=`pwd`/app


Initialize the server
.. code-block:: console
    (b2share-evolution)$ cd $VIRTUAL_ENV/src/b2share
    (b2share-evolution)$ # Set the env variables
    (b2share-evolution)$ source ./devenv/docker_env.sh
    (b2share-evolution)$ ./devenv/init.sh

Start the server:

.. code-block:: console
    (b2share-evolution)$ cd $VIRTUAL_ENV/src/b2share
    (b2share-evolution)$ inveniomanage runserver 
    * Running on http://localhost:4000/ (Press CTRL+C to quit)

