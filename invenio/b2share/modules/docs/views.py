"""SimpleStore Flask Blueprint"""
from flask import request, Blueprint, render_template
from flask.ext.login import login_required
from invenio.base.i18n import _
# import invenio.b2share.modules.b2deposit.simplestore_upload_handler as uph
# import invenio.b2share.modules.b2deposit.simplestore_deposit_handler as dep

import markdown, os
CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))

# set blueprint
blueprint = Blueprint('docs', __name__, url_prefix="/docs",  static_url_path='/docs',
                      template_folder='templates', static_folder='static')


from invenio.modules.search.models import Collection


def _read_markdown_as_html(target):
    input_file = markdown.codecs.open(CURRENT_DIR + target, mode="r",
                                      encoding="utf-8")
    return markdown.markdown(input_file.read())

@blueprint.route('/b2share-about', methods=['GET'])
def b2share_about():
    html = _read_markdown_as_html("/templates/about.md")
    collection = Collection.query.get_or_404(1)
    return render_template('docs.html', markdown_render=html, collection=collection)

@blueprint.route('/b2share-tou', methods=['GET'])
def b2share_tou():
    html = _read_markdown_as_html("/templates/tou.md")
    collection = Collection.query.get_or_404(1)
    return render_template('docs.html', markdown_render=html, collection=collection)

@blueprint.route('/b2share-faq', methods=['GET'])
def b2share_faq():
    html = _read_markdown_as_html("/templates/faq.md")
    collection = Collection.query.get_or_404(1)
    return render_template('docs.html', markdown_render=html, collection=collection)

@blueprint.route('/b2share-guide', methods=['GET'])
def b2share_guide():
    html = _read_markdown_as_html("/templates/user-docs.md")
    collection = Collection.query.get_or_404(1)
    return render_template('docs.html', markdown_render=html, collection=collection)

@blueprint.route('/', methods=['GET'])
def index():
    # TODO: redirect to homepage
    pass

