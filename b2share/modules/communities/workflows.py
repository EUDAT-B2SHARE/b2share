# -*- coding: utf-8 -*-
#
# This file is part of EUDAT B2Share.
# Copyright (C) 2015, 2016, University of Tuebingen, CERN.
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

"""Publication workflows."""

from .errors import InvalidPublicationStateError

def review_and_publish_workflow(previous_model, new_deposit):
    """Workflow publishing the deposits on submission."""
    from b2share.modules.deposit.api import PublicationStates
    new_state = new_deposit['publication_state']
    previous_state = previous_model.json['publication_state']
    if previous_state != new_state:
        transition = (previous_state, new_state)
        # Check that the transition is a valid one
        if transition not in [
            (PublicationStates.draft.name, PublicationStates.submitted.name),
            (PublicationStates.submitted.name, PublicationStates.draft.name),
            (PublicationStates.submitted.name,
             PublicationStates.published.name),
        ]:
            raise InvalidPublicationStateError(
                description='Transition from publication state {0} to {1} is'
                'not allowed by community\'s workflow {2}'.format(
                    previous_state, new_state, 'review_and_publish'
                )
            )


def direct_publish_workflow(previous_model, new_deposit):
    """Workflow publishing the deposits on submission."""
    from b2share.modules.deposit.api import PublicationStates

    new_state = new_deposit['publication_state']
    previous_state = previous_model.json['publication_state']
    if previous_state != new_state:
        transition = (previous_state, new_state)
        # Check that the transition is a valid one
        if transition not in [
            (PublicationStates.draft.name, PublicationStates.submitted.name),
            (PublicationStates.draft.name, PublicationStates.published.name),
        ]:
            raise InvalidPublicationStateError(
                description='Transition from publication state {0} to {1} is '
                'not allowed by community\'s workflow {2}'.format(
                    previous_state, new_state, 'direct_publish'
                )
            )
    # Publish automatically when submitted
    if new_state == PublicationStates.submitted.name:
        new_deposit['publication_state'] = PublicationStates.published.name


publication_workflows = {
    'review_and_publish': review_and_publish_workflow,
    'direct_publish': direct_publish_workflow,
}
