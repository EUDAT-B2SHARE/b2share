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

"""B2Share cli commands for records."""


from __future__ import absolute_import, print_function

import click
from flask_cli import with_appcontext

from invenio_db import db
from invenio_pidstore.models import PIDStatus
from invenio_pidstore.providers.datacite import DataCiteProvider

from b2share.modules.records.serializers import datacite_v31
from b2share.modules.records.minters import make_record_url
from b2share.modules.communities.api import Community
from b2share.modules.records.tasks import update_expired_embargos
from .utils import list_db_published_records


@click.group()
def b2records():
    """B2SHARE Records commands."""


@b2records.command()
@with_appcontext
@click.option('-u', '--update', is_flag=True, default=False)
def check_dois(update):
    """ Checks that all DOIs of records in the current instance are registered.
    """
    for record in list_db_published_records():
        check_record_doi(record, update)


@b2records.command()
@with_appcontext
def update_expired_embargoes():
    """Updates all records with expired embargoes to open access."""
    update_expired_embargos.delay()
    click.secho('Expiring embargoes...', fg='green')


def check_record_doi(record, update=False):
    """ Checks that the DOI of a record is registered."""
    recid = record.get('_deposit', {}).get('id')
    click.secho('checking DOI for record {}'.format(recid))
    doi_list = [DataCiteProvider.get(d.get('value'))
                for d in record['_pid']
                if d.get('type') == 'DOI']
    for doi in doi_list:
        click.secho('    {}: {}'.format(doi.pid.pid_value, doi.pid.status))
        if doi.pid.status != PIDStatus.RESERVED:
            continue

        # RESERVED but not REGISTERED
        if update:
            url = make_record_url(recid)
            doc = datacite_v31.serialize(doi.pid, record)
            doi.register(url=url, doc=doc)
            db.session.commit()
            click.secho('    registered just now', fg='green', bold=True)
        else:
            click.secho('    not registered', fg='red', bold=True)
