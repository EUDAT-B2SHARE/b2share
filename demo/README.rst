..
    This file is part of B2Share.
    Copyright (C) 2016 CERN.

    B2Share is free software; you can redistribute it
    and/or modify it under the terms of the GNU General Public License as
    published by the Free Software Foundation; either version 2 of the
    License, or (at your option) any later version.

    B2Share is distributed in the hope that it will be
    useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
    General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with B2Share; if not, write to the
    Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
    MA 02111-1307, USA.

    In applying this license, CERN does not
    waive the privileges and immunities granted to it by virtue of its status
    as an Intergovernmental Organization or submit itself to any jurisdiction.

======================
 B2Share Demonstration
======================

This file describes how to install and use this B2Share demonstration.

Prerequisites
=============

This demonstration module needs b2share to be installed.

The database must be initalized. Run these commands if this is not the case.

.. code-block:: console
    $ # Run these commands in b2share directory.
    $ b2share db init
    $ b2share db create

Demonstration Installation
==========================

.. code-block:: console
    $ # Run this command in b2share/demo directory.
    $ pip install -e .

Now the b2share command has been extended and we can load the demo.

.. code-block:: console
    $ # Run this command in b2share/demo directory.
    $ # load the demo data
    $ b2share demo load

Demonstration usage
===================

The B2Share command works as before. You can just run the application.

.. code-block:: console
    $ b2share run
