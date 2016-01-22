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

"""SimpleStore Flask Blueprint"""
from flask import Blueprint, render_template
from flask.ext.breadcrumbs import register_breadcrumb
from invenio_base.i18n import _
from flask import redirect

import markdown, os
CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))

blueprint = Blueprint('docs', __name__, url_prefix="/docs",  static_url_path='/docs',
                      template_folder='templates', static_folder='static')

from invenio_collections.models import Collection


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
