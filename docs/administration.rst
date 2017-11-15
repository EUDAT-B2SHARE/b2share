.. This file is part of EUDAT B2Share.
   Copyright (C) 2017, CERN, University of Tübingen.

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


Administration
==============

SuperAdministrator
------------------

The superadministrator right allows a particular user to run any B2SHARE
operation. Please be careful in assigning it.

All operations below will try to identify the user based on the email address.
The user must have logged in into B2SHARE at least once, otherwise the email
address will not be found in the database.

**Add superadministrator rights**:

.. code-block:: console

    $ b2share access allow -e <email_address_of_user> superuser-access

**Revoke superadministrator rights**:

.. code-block:: console

    $ b2share access remove -e <email_address_of_user> superuser-access

**List existing rights**:

.. code-block:: console

    $ b2share access show -e <email_address_of_user>


Communities
-----------

B2SHARE has special command-line interface (CLI) commands to create and edit
communities.

To **list all communities**, run:

.. code-block:: console

    $ b2share communities list

To **create a community**, make sure that B2SHARE_UI_PATH is defined in your
environment and points to the b2share ``.../webui/app`` folder, and
then run:

.. code-block:: console

    $ b2share communities create <name> <description> <logo_file_name>

The <logo_file_name> parameter must be the filename of an image file, already
located in the ``$B2SHARE_UI_PATH/img/communities/`` directory.

To **edit a community**, use the ``b2share communities edit`` command, with
the necessary arguments. For more information run:

.. code-block:: console

    $ b2share communities edit --help

After a community name or description is updated, please make sure to also run
the following command, which synchronizes the list of communities with the
OAI-PMH declared sets:

.. code-block:: console

    $ b2share oai update_sets

Community Admin
---------------

Each B2SHARE record is assigned to a community. A community administrator has
certain special rights, like the right to edit a published record's metadata
and the right to add members to the community.

To **assign the community administrator role for a user**, do the following:

1. Find the unique ID of the community, using the HTTP API, by going to
https://YOUR_B2SHARE/api/communities (for example, the community id can be
``8d963a295e19492b8cfe97da4f54fad2``). The administrator role for this
community will be ``com:COMMUNITY_ID:admin`` (please use the actual community
id between colons).

2. Run the following b2share command:

.. code-block:: console

    $ b2share roles add <email_address_of_user> com:COMMUNITY_ID:admin

CLI for community mgt
---------------------
1. Create a community 

.. code-block:: console

    $ b2share communities create NAME DESCRIPTION FILE

File can be some webformat logo.

2. Create a schema (look in demo/b2share_demo/data/communities for inspiration)
   $ b2share communities set_schema COMMUNITY SCHEMAFILE
   
Note: you can also look in tests/b2share_functional_tests/data/testschema.py
Note: you can also do

.. code-block:: console

  $ b2share schemas block_schema list    #to obtain ID
  $ b2share schemas block_schema_version_generate_json BLOCK_SCHEMA_ID 

The last command generates a schema that you can adapt according to the rules of json_schema.


Fine-grained access controls
----------------------------

Warning: Please only run the following commands if instructed to do so by a B2SHARE representative:

1. Allow the community administrator role to update record metadata (this is
enabled by default when a community is created):

.. code-block:: console

    $ b2share access allow -r com:COMMUNITY_ID:admin update-record-metadata -a '{"community":"COMMUNITY_ID_WITH_DASHES"}'

For example:

.. code-block:: console

    $ b2share access allow -r com:8d963a295e19492b8cfe97da4f54fad2:admin update-record-metadata -a '{"community":"8d963a29-5e19-492b-8cfe-97da4f54fad2"}'


Records
-------

Delete a published Record
~~~~~~~~~~~~~~~~~~~~~~~~~

The Command Line Interface is currently missing a way to delete a record while
leaving a tombstone. This will be fixed shortly but in the mean time here is
how to delete a record. Note that the following method just marks the record
as deleted, it still keeps it in the database just in case we want to revert
the deletion. If a user access the record page after that he will see a
``410 Gone`` error code meaning that a record existed before but was deleted.

First go to the page of the record you want to delete. Look at the URL, it
should have the form ``https://<B2SHARE_HOST>/records/<RECORD_PID>``, where
``<RECORD_PID>`` is a UUID. Note this UUID, it is the persistent identifier of
this record, we will need it later.

Next we open the b2share shell. This shell executes python code as B2SHARE.
Be careful as any action is performed directly on the database.

.. code-block:: console

    $ b2share shell

In the shell we will start by retrieving the record using the persistent
identifier.

.. code-block:: python

    >>> from invenio_pidstore.models import PersistentIdentifier
    >>> from invenio_records_files.api import Record
    >>> pid = PersistentIdentifier.get('b2rec', '<RECORD_PID>')
    >>> record = Record.get_record(pid.object_uuid)

Where ``<RECORD_PID>`` should be replaced with the record persistent identifier.

Now we retrieve all the other persistent identifiers attached to that record

.. code-block:: python

    >>> pids = PersistentIdentifier.query.filter_by(object_type='rec', object_uuid=pid.object_uuid).all()

Now we mark the record as deleted.

.. code-block:: python

    >>> record.delete()

We also need to mark all the persistent identifier as deleted so that the
proper error message is returned to users. As this is python code you must
keep the indentation as shown bellow.

.. code-block:: python

    >>> for pid in pids:
    ...     pid.unassign()
    ...     pid.delete()

Finally we commit our changes to the database.

.. code-block:: python

    >>> from invenio_db import db
    >>> db.session.commit()

If you go the record webpage you should now see the `410` error message.

Note that we didn't delete the deposit. Everything is kept in the database
and can be reverted if need be. The files are not removed either.


Upgrade B2SHARE
---------------

From version 2.1.0 on B2SHARE can be upgraded by running

.. code-block:: console

    $ b2share upgrade run
