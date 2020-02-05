.. This file is part of EUDAT B2Share.
   Copyright (C) 2018 CERN.

   B2Share is free software; you can redistribute it and/or
   modify it under the terms of the GNU General Public License as
   published by the Free Software Foundation; either version 2 of the
   License, or (at your option) any later version.

   B2Share is distributed in the hope that it will be useful, but
   WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
   General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with B2Share; if not, write to the Free Software Foundation, Inc.,
   59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

   In applying this license, CERN does not
   waive the privileges and immunities granted to it by virtue of its status
   as an Intergovernmental Organization or submit itself to any jurisdiction.

B2SHARE architecture
====================

.. automodule:: b2share

1. B2SHARE factory
------------------

.. automodule:: b2share.factory

2. B2SHARE modules
------------------

B2SHARE is customizing Invenio modules and adds some other custom modules. You
can find all these modules in the `b2share.modules` package. The files they
contain follow Invenio convention:

* ext.py: the Flask extension class initializing the module.
* models.py: defines the database models.
* views.py: defines the REST API.
* serializers.py: serializers used for REST API responses.
* links.py: function generating links to resources. This is used by the
  serializers.
* loaders.py: defines functions loading input from REST API requests.
* permissions.py: defines access control. It is used by the REST API.



2.1 Users
~~~~~~~~~

.. automodule:: b2share.modules.users

2.2 Communities
~~~~~~~~~~~~~~~

.. automodule:: b2share.modules.communities

2.2 Records
~~~~~~~~~~~

.. automodule:: b2share.modules.records


2.3 Deposits
~~~~~~~~~~~~

.. automodule:: b2share.modules.deposit


2.4 Schemas
~~~~~~~~~~~

.. automodule:: b2share.modules.schemas


2.5 Files
~~~~~~~~~

.. automodule:: b2share.modules.files


2.6 Stats
~~~~~~~~~

.. automodule:: b2share.modules.stats


2.7 Remotes
~~~~~~~~~~~

.. automodule:: b2share.modules.remotes


2.8 Oauthclient
~~~~~~~~~~~~~~~

.. automodule:: b2share.modules.oauthclient


2.9 OAIServer
~~~~~~~~~~~~~

.. automodule:: b2share.modules.oaiserver


2.10 Handle
~~~~~~~~~~~

.. automodule:: b2share.modules.handle


2.11 Access
~~~~~~~~~~~

.. automodule:: b2share.modules.access


2.12 upgrade
~~~~~~~~~~~~

.. automodule:: b2share.modules.upgrade


2.13 ApiRoot
~~~~~~~~~~~~

.. automodule:: b2share.modules.apiroot


3. B2SHARE CELERY
-----------------

This module creates the application used by celery.

Example:

::

    $ B2SHARE_JSONSCHEMAS_HOST='localhost:5000' celery worker -A b2share.celery --loglevel="DEBUG"

4. wsgi
-------

This module provides the WSGI application used by UWSGI when it runs the
B2SHARE REST API service, i.e. B2SHARE backend.

5. config
---------

B2SHARE default configuration. Some of its variable are overriden by the
flask application instance configuration when it runs in the docker container.
See Flask and Invenio documentation for more information.
