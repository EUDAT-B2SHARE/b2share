
from elasticsearch_dsl import Q, TermsFacet

from flask import has_request_context
from flask_login import current_user

from invenio_search import RecordsSearch
from invenio_search.api import DefaultFilter

from invenio_deposit.permissions import admin_permission_factory


def deposits_filter():
    """Filter list of deposits.

    Permit to the user to see all if:

    * The user is an admin (see
        func:`invenio_deposit.permissions:admin_permission_factory`).

    * It's called outside of a request.

    Otherwise, it filters out any deposit where user is not the owner.
    """
    if not has_request_context() or admin_permission_factory().can():
        return Q()
    else:
        return Q(
            'match', **{'_deposit.owners': getattr(current_user, 'id', 0)}
        )


class DepositSearch(RecordsSearch):
    """Default search class."""

    class Meta:
        """Configuration for deposit search."""

        index = 'deposits'
        doc_types = None
        fields = ('*', )
        facets = {
            'status': TermsFacet(field='_deposit.status'),
        }
        default_filter = DefaultFilter(deposits_filter)