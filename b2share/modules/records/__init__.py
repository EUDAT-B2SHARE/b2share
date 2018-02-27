# -*- coding: utf-8 -*-
#
# This file is part of EUDAT B2Share.
# Copyright (C) 2016 University of Tuebingen, CERN.
# Copyright (C) 2015 University of Tuebingen.
#
# B2Share is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# B2Share is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with B2Share; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""B2SHARE Records

Records are the internal reprensentation of a dataset. This module specifically
focuses on published datasets. See `b2share.modules.deposits` for draft
datasets. See the training documentation. It explains the record publication
workflow.

The module ``b2share.modules.records`` customizes how Invenio records and its
persistent Identifiers behave.

Persistent Identifiers
^^^^^^^^^^^^^^^^^^^^^^

.. graphviz::

    digraph G {
        rankdir=TB;

        record [
            label=<<TABLE BORDER="1" CELLBORDER="1" cellpadding="10">
                <TR><TD><B>Published Record</B></TD></TR>
                <TR><TD PORT="id">+ internal ID: UUID</TD></TR>
                </TABLE>>
            shape = "none"
        ];
        b2rec [
            label=<<TABLE BORDER="1" CELLBORDER="1" cellpadding="10">
                <TR>
                    <TD ALIGN="LEFT"><B>"b2rec" Persistent Identifier</B></TD>
                </TR>
                <TR><TD>
                    <TABLE BORDER="0">
                        <TR><TD ALIGN="LEFT">+ pid_type: "b2rec"</TD></TR>
                        <TR><TD ALIGN="LEFT" PORT="value">+ pid_value: "Record UUID"</TD></TR>
                    </TABLE>
                </TD></TR>
                </TABLE>>
            shape = "none"
        ];
        oai [
            label=<<TABLE BORDER="1" CELLBORDER="1" cellpadding="10">
                <TR>
                    <TD ALIGN="LEFT"><B>OAI Persistent Identifier</B></TD>
                </TR>
                <TR><TD>
                    <TABLE BORDER="0">
                        <TR><TD ALIGN="LEFT">+ pid_type: "oai"</TD></TR>
                        <TR><TD ALIGN="LEFT" PORT="value">+ pid_value: "Record UUID"</TD></TR>
                    </TABLE>
                </TD></TR>
                </TABLE>>
            shape = "none"
        ];
        b2rec:value -> record;
        oai:value -> record;
    }


In the rest of the documentation we will call Persistent Identifiers as "PID".
A PID is a unique identifier which can be used to reference a record or another
resource. A record has multiple persistent identifiers. See
``invenio-pidstore`` for more information.

A record contains metadata in a JSON format and references some files.

In B2SHARE we create a **"b2rec" PID** for each and every
record. This **internal Persistent Identifier** is used in the REST API
endpoint giving access to the record: ``/api/records/<b2rec PID>``.

Records are validated using a **JSON Schema**. See the ``b2share.schema``
module for more information.

Records belong to a **community**. The first thing a user does when he creates
a draft record is to select the community it will belong to. See the
``b2share.communities`` module for more information. The community provides
the JSON Schema validating the record.

Record versioning
^^^^^^^^^^^^^^^^^

One of the most important rules in B2SHARE is that **files cannot be changed
for published records**. Otherwise a researcher would not be able to see the
dataset as it was first published. However it is possible to create multiple
versions of a record. Records are versioned using ``invenio-pidrelations``.

Each record has a **parent PID** (sometime called **HEAD PID**) which
references the "b2rec" PID of each version of a record.

.. graphviz::

    digraph G {
        rankdir=TB;

        parent [
            label="Parent b2rec PID"
            shape="rectangle"
        ];
        b2rec1 [
            label="b2rec PID"
            shape="rectangle"
        ];
        b2rec2 [
            label="b2rec PID"
            shape="rectangle"
        ];
        b2rec3 [
            label="b2rec PID"
            shape="rectangle"
        ];
        reserved_b2rec [
            label="RESERVED b2rec PID for the next publication"
            shape="rectangle"
        ];
        b2dep [
            label="b2dep PID (see deposit)"
            shape="rectangle"
        ];
        record1 [
            label="record version 1"
        ];
        record2 [
            label="record version 2"
        ];
        record3 [
            label="record version 3"
        ];
        b2rec1->record1
        b2rec2->record2
        b2rec3->record3
        parent->b2rec1
        parent->b2rec2
        parent->b2rec3
        parent->reserved_b2rec
        reserved_b2rec->b2dep
    }

You will see that **draft records**, also known as **deposits**, also have
their own PIDs, with type **b2dep**. Whenever a draft record is created,
the HEAD PID also keeps a reference to the b2rec PID which will be used by the
next published record.

A Record also contains other Persistent Identifier values in its JSON metadata
in the ``_pid`` key. This is a choice for simplicity but could change in the
future. Those PIDs are:

* an **ePIC_PID**: PID used in EUDAT. Its a Handle.net PID which references
  every file and dataset in EUDAT services. There is one ePIC_PID per record.
* a **DOI**: These PIDs are very common in research publications, and thus have
  been added.

Those PIDs are **minted** in a record when it is published. Minting a record
just means writing the PID value in its metadata, creating a clear link in
the database. Minted PIDs can be retrieved using the appropriate fetcher
functions. See ``minters.py`` and ``fetchers.py``.

Record Access Control
^^^^^^^^^^^^^^^^^^^^^

See ``b2share.modules.records.permissions``.

A record belongs to a user, which is for now the one who created it.

The different actions which can be performed on a published record are:

* **update the metadata**: allowed to its owner and the administrator of the
  community owning the record.
* **delete the record**: only ``superuser`` can do it. Records should be
  deleted only in case of legal issues (ex: copyright infringement).
* **read a record metadata**: all users can see it, even anonymous ones.
* **read a records' files**: if the record is in **open_access** then the files
  are always accessible. Otherwise the files are only accessible to the
  community administrator and the record owner (same permission as for
  updating the record's metadata).

A record can automatically switch from ``open_access=False`` to
``open_access=True`` if it is under embargo and the embargo date is in the
past. This is done by a Celery task (see ``b2share.modules.records.tasks``)


**Future Work**: B2SHARE uses B2Access for authentication but it
handles internally the access control to every record. There is in EUDAT a
"Data Policy Manager" service but it can't be used for now as we would need to
replicate the whole access control in elasticsearch. It would not be performant
to query an external service for each search result.


Records REST API
^^^^^^^^^^^^^^^^

B2SHARE uses the ``invenio-records-rest`` module in order to provide a REST
API. This REST API is customized. The modules Invenio-Records-Rest and
Invenio-deposits provide respectively the endpoints:

* ``/api/records``
* ``/api/deposits``

This enables Invenio to have different PIDs for a record and its deposit (aka draft
record): ``/api/records/<ID1>`` and ``/api/records/<ID2>`` where ``ID1``
and ``ID2`` are different. This is simplified in B2SHARE as the record and its
deposit share the same PID value (but with different types: b2rec and b2dep).
The result is a simplified API:

* ``/api/records/<ID>``: access to a record.
* ``/api/records/<ID>/draft``: access to the record's draft/deposit.

Calling ``POST /api/records/`` will create a deposit instead of a record, and
it will be available at ``/api/records/<ID>/draft``. Once the deposit is
published the new record will be available at ``/api/records/<ID>``.

In order to simplify even more, the PID value is by convention the same as the
deposit internal UUID.

See the ``b2share.modules.records.views`` module.


Record Search
^^^^^^^^^^^^^

Users can search among records. This is possible by indexing records in
Elasticsearch and using ``invenio-search`` to provide a search endpoing in
the REST API.

See ``b2share.modules.records.indexer``.
"""

from __future__ import absolute_import, print_function

from .ext import B2ShareRecords

__all__ = ('B2ShareRecords')
