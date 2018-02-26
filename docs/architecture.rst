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

.. automodule:: b2share.modules.schemas


2.8 ApiRoot
~~~~~~~~~~~

.. automodule:: b2share.modules.apiroot
