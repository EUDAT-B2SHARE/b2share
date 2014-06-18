# -*- coding: utf-8 -*-


from flask import Blueprint
from flask import make_response, g, request, flash, jsonify, \
    redirect, url_for, current_app, abort, session, Blueprint, \
    render_template
from flask.ext.menu import register_menu
from flask.ext.breadcrumbs import register_breadcrumb

from invenio.ext.template.context_processor import \
    register_template_context_processor
from invenio.base.i18n import _
from invenio.base.decorators import templated
from invenio.modules.formatter import format_record
from invenio.modules.search.models import Collection
from invenio.modules.search.forms import EasySearchForm


blueprint = Blueprint('b2share', __name__, url_prefix="",
                      template_folder='templates',
                      static_url_path='',  # static url path has to be empty
                                           # if url_prefix is empty
                      static_folder='static')

@blueprint.route('/index.html', methods=['GET', 'POST'])
@blueprint.route('/index.py', methods=['GET', 'POST'])
@blueprint.route('/', methods=['GET', 'POST'])
@templated('index.html')
@register_menu(blueprint, 'main.b2share', _('B2Share'), order=1)
@register_breadcrumb(blueprint, '.', _('Home'))
def index():
    """ Renders homepage. """

    # legacy app support
    c = request.values.get('c')
    if c == current_app.config['CFG_SITE_NAME']:
        return redirect(url_for('.index', ln=g.ln))
    elif c is not None:
        return redirect(url_for('.collection', name=c, ln=g.ln))

    collection = Collection.query.get_or_404(1)

    @register_template_context_processor
    def index_context():
        return dict(
            of=request.values.get('of', collection.formatoptions[0]['code']),
            easy_search_form=EasySearchForm(csrf_enabled=False),
            format_record=format_record,
        )
    return dict(collection=collection)
