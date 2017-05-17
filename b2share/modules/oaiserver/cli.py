# -*- coding: utf-8 -*-
#
# This file is part of EUDAT B2Share.
# Copyright (C) 2017 University of Tübingen
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
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""B2Share OAI-PMH cli commands."""


from __future__ import absolute_import, print_function

import click
from flask.cli import with_appcontext
from sqlalchemy.orm.attributes import flag_modified

from invenio_db import db
from invenio_oaiserver.models import OAISet
from invenio_records.models import RecordMetadata
from invenio_records_files.api import Record

from b2share.modules.communities.api import Community
from b2share.modules.records.utils import list_db_published_records



@click.group()
def oai():
    """OAI commands."""


@oai.command()
@with_appcontext
def update_sets():
    """Check that each community has a corresponding oai set"""
    for community in Community.get_all():
        dirty = False
        oaiset = OAISet.query.filter(OAISet.spec == str(community.id)).one_or_none()
        if not oaiset:
            click.secho('Adding new oai set {}'.format(community.name),
                        fg='yellow', bold=True)
            oaiset = OAISet(spec=str(community.id),
                            name=community.name,
                            description=community.description)
            dirty = True
        else:
            if oaiset.name != community.name:
                oaiset.name = community.name
                dirty = True
                click.secho('Update name for set {}'.format(oaiset.spec),
                            fg='yellow', bold=True)
            if oaiset.description != community.description:
                oaiset.description = community.description
                dirty = True
                click.secho('Update description for set {}'.format(oaiset.spec),
                            fg='yellow', bold=True)
        if dirty:
            db.session.add(oaiset)
    db.session.commit()


@oai.command()
@with_appcontext
def update_records_set():
    """Check that each record oai entry has a set"""
    for record in list_db_published_records():
        metadata = record.model.json
        if not metadata.get('_oai'):
            click.secho('Record {} has no _oai entry'.format(record.id),
                        fg='yellow', bold=True)
            continue
        _oai = metadata.get('_oai')
        oaiset = metadata.get('community') # community.id == setSpec
        if _oai.get('sets') != [oaiset]:
            click.secho('Add set {} to record {}'.format(oaiset, record.id),
                        fg='yellow', bold=True)
            _oai['sets'] = [oaiset]
            metadata['_oai'] = _oai
            # don't use record.commit(): it validates the record and crashes
            # when retrieving the schema, as the site certificate is invalid
            flag_modified(record.model, 'json')
            db.session.merge(record.model)
            db.session.commit()
