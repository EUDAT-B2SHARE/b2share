B2Share installation
====================

1. IMPORTANT
------------

This installation workflow is only valid for the `evolution` branch in
development mode.


2. Simplified installation
--------------------------

Install docker as specified here:
- mac https://docs.docker.com/installation/mac/
- ubuntu https://docs.docker.com/installation/ubuntulinux/


Install python and python virtualenv.
Here are the commands for mac (see 3.* for other OS):

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
    (b2share-evolution)$ # install b2share python dependencies. This will create ../invenio and
    (b2share-evolution)$ # other directories where the master branch of these repositories are
    (b2share-evolution)$ # then checkouted
    (b2share-evolution)$ pip install -r requirements.txt
    (b2share-evolution)$ cd .. && ls
    b2share			invenio			invenio-accounts	invenio-collections	invenio-oaiharvester	invenio-upgrader


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
    (b2share-evolution)$ ./devenv/init.sh
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


Open another terminal, start the server:

.. code-block:: console
    $ # Enable docker environment
    $ eval $(docker-machine env default)
    $ # Enable the virtual environment we previously created
    $ workon b2share-evolution
    (b2share-evolution)$ # Go to its working directory
    (b2share-evolution)$ cdvirtualenv src/b2share
    (b2share-evolution)$ inveniomanage runserver 
    * Running on http://localhost:4000/ (Press CTRL+C to quit)

3. Prerequisites for advanced installation
------------------------------------------

Your must be deploying on a Unix system.


3.1. Debian / Ubuntu LTS
~~~~~~~~~~~~~~~~~~~~~~~~

If you are using Ubuntu 14.10 or later, then you can install Invenio by
following this tutorial. **Note:** the recommended Python version is 3.7.5+

.. code-block:: console

    $ python --version
    Python 3.7.5+
    $ sudo apt-get update
    $ sudo apt-get install build-essential git redis-server \
                           libmysqlclient-dev libxml2-dev libxslt-dev \
                           libjpeg-dev libfreetype6-dev libtiff-dev \
                           libffi-dev libssl-dev \
                           software-properties-common python-dev \
                           virtualenvwrapper subversion
    $ sudo pip install -U virtualenvwrapper pip
    $ source .bashrc

3.1.1. MySQL
++++++++++++

MySQL Server will ask you for a password, you will need it later and we will
refer to it as ``$MYSQL_ROOT``.

.. code-block:: console

    $ sudo apt-get install mysql-server

3.1.2. Node.js
++++++++++++++

`node.js <http://nodejs.org/>`_ and `npm <https://www.npmjs.org/>`_ from Ubuntu
are troublesome so we recommend you to install them from Chris Lea's PPA.

.. code-block:: console

    $ sudo add-apt-repository ppa:chris-lea/node.js
    $ sudo apt-get update
    $ sudo apt-get install nodejs

3.2. Centos / RHEL
~~~~~~~~~~~~~~~~~~

If you are using Redhat, Centos or Scientific Linux this will setup everything
you need. We are assuming that sudo has been installed and configured nicely.

.. code-block:: console

    $ python --version
    3.6.6
    $ sudo yum update
    $ sudo rpm -Uvh http://mirror.switch.ch/ftp/mirror/epel/6/i386/epel-release-6-8.noarch.rpm
    $ sudo yum -q -y groupinstall "Development Tools"
    $ sudo yum install git wget redis python-devel \
                       mysql-devel libxml2-devel libxslt-devel \
                       python-pip python-virtualenvwrapper
    $ sudo service redis start
    $ sudo pip install -U virtualenvwrapper pip
    $ source /usr/bin/virtualenvwrapper.sh

3.2.1. MySQL
++++++++++++

Setting up MySQL Server requires you to give some credentials for the root
user. You will need the root password later on and we will refer to it as
``$MYSQL_ROOT``.

If you are on CentOS 7, the mysql-server package is not available in the
default repository. First we need to add the official YUM repository provided
by Oracle. The YUM repository configuration can be downloaded from the `MySQL
website <http://dev.mysql.com/downloads/repo/yum/>`_. Choose the desired
distribution (Red Hat Enterprise Linux 7 / Oracle Linux 7 for CentOS 7) and
click Download.
The download link can be retrieved without registering for an Oracle account.
Locate the "No thanks, just start my download" link and pass the link URL as a
parameter to rpm.

.. code-block:: console

    # only needed with CentOS version >= 7
    $ sudo rpm -Uvh http://dev.mysql.com/get/mysql-community-release...

    # for every CentOS version
    $ sudo yum install mysql-server
    $ sudo service mysqld status
    mysqld is stopped
    $ sudo service mysqld start
    $ sudo mysql_secure_installation
    # follow the instructions

3.2.2. Node.js
++++++++++++++

Node.js requires a bit more manual work to install it from the sources. We are
following the tutorial: `digital ocean: tutorial on how to install node.js on
centor
<https://www.digitalocean.com/community/tutorials/how-to-install-and-run-a-node-js-app-on-centos-6-4-64bit>`_

.. code-block:: console

    $ mkdir opt
    $ cd opt
    $ wget http://nodejs.org/dist/v0.10.29/node-v0.10.29.tar.gz
    $ tar xvf node-v0.10.29.tar.gz
    $ cd node-v0.10.29
    $ ./configure
    $ make
    $ sudo make install
    $ node --version
    v0.10.29
    $ npm --version
    1.4.14


.. _OS X:


3.3. OS X
~~~~~~~~~~

The steps below can be used to install Invenio on a machine running OS X 10.9 or later.

First, we need to install the `Homebrew <http://brew.sh/>`_ package manager.
Follow the installation procedure by running following command:

.. code-block:: console

    $ ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"

You need to check that ``/usr/local/bin`` occurs before the ``/usr/bin``, otherwise you can
try following commands:

.. code-block:: console

    $ echo export PATH="/usr/local/bin:$PATH" >> ~/.bash_profile
    $ source ~/.bash_profile (to reload the profile)

Next, you should check if everything is up-to-date!

.. code-block:: console

    $ brew update
    $ brew doctor
    $ brew upgrade

Now, it is time to start installing the prerequisites.

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

Save the file and reload it by typing:

.. code-block:: console

    $ source ~/.bash_profile

and continue with the installation of prerequisite packages:

.. code-block:: console

    $ brew install redis


.. note::

    See `MySQL on OS X`_ for installing ``mysql``.

In order to install ``libxml2`` and ``libxslt`` packages run:

.. code-block:: console

    $ brew install automake autoconf libtool libxml2 libxslt
    $ brew link --force libxml2 libxslt

The following might not be necessary but is good to have for completeness.

.. code-block:: console

    $ brew install libjpeg libtiff freetype libffi xz
    $ pip install -I pillow

Install ``node`` by following `Node on OS X`_

For ``bower``, type:

.. code-block:: console

    $ npm install -g bower

After the configuration section install the following(required for the assets):

.. code-block:: console

    $ npm install -g less clean-css requirejs uglify-js

See the following sections `Installation`_ , `Configuration`_ and `Development`_
The commands for ``OS X`` are the same as in ``Linux``.

.. note::

    When initializing the database, type:

    .. code-block:: console

        $ inveniomanage database init --user=root --yes-i-know (because we have no root password)

.. note::

    For developers, honcho is recommended and will make your life
    easier because it launches all the servers together as it finds the ``Procfile``.

.. _MySQL on OS X:

3.4.1. MySQL
++++++++++++

We will install MySQL but without a root password.
It should be easy to set the root password once you are connected in MySQL.

.. code-block:: console

    $ brew install mysql
    $ unset TMPDIR
    $ mysql_install_db --verbose --user=`whoami` \
     --basedir="$(brew --prefix mysql)" \
     --datadir=/usr/local/var/mysql \
     --tmpdir=/tmp

You can start, stop, or restart MySQL server by typing:

.. code-block:: console

    $ mysql.server (start | stop | restart)


.. _Node on OS X:

3.4.2. Node.js
++++++++++++++

Install ``node`` by typing:

.. code-block:: console

    $ brew install node


3.4. Extra tools
~~~~~~~~~~~~~~~~

3.4.1. Bower
++++++++++++

Bower is used to manage the static assets such as JavaScript libraries (e.g.,
jQuery) and CSS stylesheets (e.g., Bootstrap). It's much easier to install them
globally (``-g``) but you're free to choose your preferred way.

.. code-block:: console

    # global installation
    $ sudo su -c "npm install -g bower"
    # user installation
    $ npm install bower


3.4.2 ``git-new-workdir`` (optional)
++++++++++++++++++++++++++++++++++++

For the rest of the tutorial you may want to use ``git-new-workdir``. It's a
tool that will let you working on the same repository from different locations.
Just like you would do with subversion branches.

.. code-block:: console

    $ mkdir -p $HOME/bin
    $ which git-new-workdir || { \
         wget https://raw.github.com/git/git/master/contrib/workdir/git-new-workdir \
         -O $HOME/bin/git-new-workdir; chmod +x $HOME/bin/git-new-workdir; }

**NOTE:** Check that ``~/bin`` is in your ``$PATH``.

.. code-block:: console

    $ export PATH+=:$HOME/bin


.. _Installation:

3. Installation
---------------------

The first step of the installation is to download the development version of
EUDAT-B2SHARE/Invenio and EUDAT-B2SHARE/B2Share.

.. code-block:: console.. code-block:: console

    $ mkdir -p $HOME/src
    $ cd $HOME/src/
    $ git clone git@github.com:EUDAT-B2SHARE/invenio.git
    $ git clone git@github.com:EUDAT-B2SHARE/b2share.git

We recommend to work using
`virtual environments <http://www.virtualenv.org/>`_ so packages are installed
locally and it will make your life easier. ``(b2share-evolution)$`` tells your
that the *b2share-evolution* environment is the active one.

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

Let's put Invenio and B2Share in the environment just created.

.. code-block:: console

    (b2share-evolution)$ cdvirtualenv
    (b2share-evolution)$ mkdir src
    (b2share-evolution)$ cd src
    (b2share-evolution)$ git-new-workdir $HOME/src/b2share/ b2share evolution
    (b2share-evolution)$ git-new-workdir $HOME/src/invenio/ invenio b2share-evolution

If you don't want to use the ``git-new-workdir`` way, you can either:

- create a symbolic link,
- or clone the repository directly into the virtualenv.

Installing Invenio.

.. code-block:: console

    (b2share-evolution)$ cdvirtualenv src/invenio
    (b2share-evolution)$ pip install -e .[development]


As Invenio is installed in development mode, you will need to compile the
translations manually.

.. code-block:: console

    (b2share-evolution)$ python setup.py compile_catalog

.. note:: Translation catalog is compiled automatically if you install
    using `python setup.py install`.

Installing B2Share. ``exists-action i`` stands for `ignore`, it means
that it'll will skip any previous installation found. Because the B2Share
depends on Invenio, it would have tried to reinstall it without this
option. If you omit it, ``pip`` will ask you what action you want to take.

.. code-block:: console

    (b2share-evolution)$ cdvirtualenv src/b2share
    (b2share-evolution)$ pip install -r requirements.txt --exists-action i


Installing the required assets (JavaScript, CSS, etc.) via bower. The file
``.bowerrc`` is configuring where bower will download the files and
``bower.json`` what libraries to download.

.. code-block:: console

    (b2share-evolution)$ inveniomanage bower -i bower-base.json > bower.json
    (b2share-evolution)$ bower install



The last step, which is very important will be to collect all the assets, but
it will be done after the configuration step.


.. _Configuration:

4.2. Configuration
~~~~~~~~~~~~~~~~~~

Generate the secret key for your installation.

.. code-block:: console

    (b2share-evolution)$ inveniomanage config create secret-key

If you are planning to develop locally in multiple environments please run
the following commands.

.. code-block:: console

    (b2share-evolution)$ # sanitaze for usage as database name and user
    (b2share-evolution)$ export SAFE_NAME=b2share_evolution
    (b2share-evolution)$ inveniomanage config set CFG_EMAIL_BACKEND flask_email.backends.console.Mail
    (b2share-evolution)$ inveniomanage config set CFG_BIBSCHED_PROCESS_USER $USER
    (b2share-evolution)$ inveniomanage config set CFG_DATABASE_NAME $SAFE_NAME
    (b2share-evolution)$ inveniomanage config set CFG_DATABASE_USER $SAFE_NAME
    (b2share-evolution)$ inveniomanage config set CFG_SITE_URL http://localhost:4000
    (b2share-evolution)$ inveniomanage config set CFG_SITE_SECURE_URL http://localhost:4000

Assets in non-development mode may be combined and minified using various
filters (see :ref:`ext_assets`). We need to set the path to the binaries if
they are not in the environment ``$PATH`` already.

.. code-block:: console

    # Local installation (using package.json)
    (b2share-evolution)$ cdvirtualenv src/invenio
    (b2share-evolution)$ npm install
    (b2share-evolution)$ inveniomanage config set LESS_BIN `find $PWD/node_modules -iname lessc | head -1`
    (b2share-evolution)$ inveniomanage config set CLEANCSS_BIN `find $PWD/node_modules -iname cleancss | head -1`
    (b2share-evolution)$ inveniomanage config set REQUIREJS_BIN `find $PWD/node_modules -iname r.js | head -1`
    (b2share-evolution)$ inveniomanage config set UGLIFYJS_BIN `find $PWD/node_modules -iname uglifyjs | head -1`

All the assets that are spread among every invenio module or external libraries
will be collected into the instance directory. By default, it create copies of
the original files. As a developer you may want to have symbolic links instead.

.. code-block:: console

    (b2share-evolution)$ inveniomanage config set COLLECT_STORAGE flask_collect.storage.link
    (b2share-evolution)$ inveniomanage collect


Once you have everything installed, you can create the database and populate it
with demo records.

.. code-block:: console

    (b2share-evolution)$ inveniomanage database init --user=root --password=$MYSQL_ROOT --yes-i-know
    (b2share-evolution)$ inveniomanage database create



.. _B2Share_Specific:

4.2. B2Share Specific
~~~~~~~~~~~~~~~~~~~~~

B2Share still needs some additional commands to be run.

.. code-block:: console
    (b2share-evolution)$ dbexec < ./install/_collections.sql
    (b2share-evolution)$ python b2share/upgrades/b2share_2015_06_23_create_domain_admin_groups.py


.. _Bibsched:

4.3. Start BibSched tasks
~~~~~~~~~~~~~~~~~~~~~

Start the bibsched processes.

.. code-block:: console
   (b2share-evolution)$ bibindex -f50000 -s5m -uadmin
   (b2share-evolution)$ # another bibindex scheduling for global index because it is a virtual index
   (b2share-evolution)$ bibindex -w global -f50000 -s5m -uadmin
   (b2share-evolution)$ bibreformat -oHB -s5m -uadmin
   (b2share-evolution)$ webcoll -v0 -s5m -uadmin
   (b2share-evolution)$ bibrank -f50000 -s5m -uadmin
   (b2share-evolution)$ bibsort -s5m -uadmin

You can check if bibsched is in automatic mode.

.. code-block:: console
   (b2share-evolution)$ bibsched

In automatic mode the top bar and bottom bar are green. In manual mode they are
grey. Press `A` to change the mode.

.. _Run_B2Share:

4.2. Run B2Share
~~~~~~~~~~~~~~~~


Now you should be able to run the development server. Invenio uses
`Celery <http://www.celeryproject.org/>`_ and `Redis <http://redis.io/>`_
which must be running alongside with the web server.

.. code-block:: console

    # make sure that redis is running
    $ sudo service redis-server status
    redis-server is running
    # or start it with start
    $ sudo service redis-server start

    # launch celery
    $ workon b2share-evolution
    (b2share-evolution)$ celery worker -E -A invenio.celery.celery --workdir=$VIRTUAL_ENV

    # in a new terminal
    $ workon invenio
    (b2share-evolution)$ inveniomanage runserver
     * Running on http://0.0.0.0:4000/
     * Restarting with reloader

.. note::

    On OS X, the command ``service`` might not be found when starting the redis
    server. To run redis, just type:

    .. code-block:: console

        $ redis-server

**Simpler way to start all services**
As a developer, you may want to use the provided
``Procfile`` with `honcho <https://pypi.python.org/pypi/honcho>`_. It
starts all the services at once with nice colors. By default, it also runs
`flower <https://pypi.python.org/pypi/flower>`_ which offers a web interface
to monitor the *Celery* tasks.

.. code-block:: console

    (b2share-evolution)$ pip install honcho flower
    (b2share-evolution)$ cdvirtualenv src/b2share
    (b2share-evolution)$ honcho start

5. Credits
----------

This manual has been heavily inspired by Invenio manual.
