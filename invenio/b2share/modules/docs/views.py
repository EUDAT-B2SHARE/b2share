"""SimpleStore Flask Blueprint"""
from flask import Blueprint, render_template
from flask.ext.breadcrumbs import register_breadcrumb
from invenio.base.i18n import _
from flask import redirect

import markdown, os
CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))

blueprint = Blueprint('docs', __name__, url_prefix="/docs",  static_url_path='/docs',
                      template_folder='templates', static_folder='static')


from invenio.modules.search.models import Collection


def _read_markdown_as_html(target):
    input_file = markdown.codecs.open(CURRENT_DIR + target, mode="r",
                                      encoding="utf-8")
    return markdown.markdown(input_file.read())

@blueprint.route('/b2share-about', methods=['GET'])
@register_breadcrumb(blueprint, 'breadcrumbs.about', _('About'))
def b2share_about():
    html = _read_markdown_as_html("/templates/about.md")
    collection = Collection.query.get_or_404(1)
    return render_template('docs.html', markdown_render=html, collection=collection)

@blueprint.route('/b2share-tou', methods=['GET'])
@register_breadcrumb(blueprint, 'breadcrumbs.tou', _('Terms of Use'))
def b2share_tou():
    html = _read_markdown_as_html("/templates/tou.md")
    collection = Collection.query.get_or_404(1)
    return render_template('docs.html', markdown_render=html, collection=collection)

@blueprint.route('/b2share-faq', methods=['GET'])
@register_breadcrumb(blueprint, 'breadcrumbs.faq', _('FAQ'))
def b2share_faq():
    html = _read_markdown_as_html("/templates/faq.md")
    collection = Collection.query.get_or_404(1)
    return render_template('docs.html', markdown_render=html, collection=collection)

@blueprint.route('/b2share-guide', methods=['GET'])
@register_breadcrumb(blueprint, 'breadcrumbs.guide', _('Guide'))
def b2share_guide():
    html = _read_markdown_as_html("/templates/user-docs.md")
    collection = Collection.query.get_or_404(1)
    return render_template('docs.html', markdown_render=html, collection=collection)

@blueprint.route('/b2share-rest-api', methods=['GET'])
@register_breadcrumb(blueprint, 'breadcrumbs.rest-api', _('REST-API'))
def b2share_rest_api():
    html = _read_markdown_as_html("/templates/rest-api.md")
    collection = Collection.query.get_or_404(1)
    return render_template('docs.html', markdown_render=html, collection=collection)

@blueprint.route('/', methods=['GET'])
def index():
    return redirect("/")
