# -*- coding: utf-8 -*-


from flask import Blueprint, g, request, redirect, url_for, current_app

import os

from invenio.ext.template.context_processor import \
    register_template_context_processor, template_args
from invenio.base.decorators import templated
from invenio.modules.formatter import format_record
from invenio.modules.search.models import Collection
from invenio.modules.search.forms import EasySearchForm
from invenio.modules.search.views.search import collection



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

    from invenio.b2share.modules.b2deposit.latest_deposits import get_latest_deposits
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



# list all domain logos in this module's static assets folder
domain_logos = [ img for img in os.listdir(os.path.join(blueprint.static_folder, 'img'))
                if img.startswith('domain-') ]

@template_args(collection)
def domain_collection_helpers():
    """Add helpers to the '/collection' templates"""
    def get_domain_icon(collection_name):
        """Return the url to the given domain collection logo if it exists"""
        if not collection_name or not isinstance(collection_name, basestring):
            return;
        logo_file_prefix = 'domain-' + collection_name.lower()
        matching_logo = [ logo for logo in domain_logos if logo.startswith(logo_file_prefix)]
        if len(matching_logo) == 1:
            return url_for('static', filename=os.path.join('img',
                                                           matching_logo[0]))
        elif len(matching_logo) > 0:
            raise Exception('multiple logos matching domain collection ' +
                            collection_name)
    return { 'get_domain_icon': get_domain_icon }
