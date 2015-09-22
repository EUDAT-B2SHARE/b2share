# -*- coding: utf-8 -*-


from flask import Blueprint, g, request, redirect, url_for, current_app

from invenio_ext.template.context_processor import \
    register_template_context_processor
from invenio_base.decorators import templated
from invenio_formatter import format_record
from invenio_collections.models import Collection
from invenio_search.forms import EasySearchForm


blueprint = Blueprint('main', __name__, url_prefix="",
                      template_folder='templates',
                      static_url_path='',  # static url path has to be empty
                                           # if url_prefix is empty
                      static_folder='static')

@blueprint.route('/', methods=['GET', 'POST'])
@templated('index.html')
def index():
    """ Renders homepage. """

    # legacy app support
    c = request.values.get('c')
    if c == current_app.config['CFG_SITE_NAME']:
        return redirect(url_for('.index', ln=g.ln))
    elif c is not None:
        return redirect(url_for('.collection', name=c, ln=g.ln))

    collection = Collection.query.get_or_404(1)

    from b2share.modules.b2deposit.latest_deposits import get_latest_deposits
    latest_deposits = get_latest_deposits()

    func = current_app.config.get("CFG_SITE_FUNCTION") or ""

    @register_template_context_processor
    def index_context():
        return dict(
            of=request.values.get('of', collection.formatoptions[0]['code']),
            easy_search_form=EasySearchForm(csrf_enabled=False),
            format_record=format_record,
        )
    return dict(collection=collection,latest_deposits=latest_deposits, pagetitle="EUDAT B2SHARE",site_function=func)
