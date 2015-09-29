# -*- coding: utf-8 -*-

# This blueprint serves the ui-frontend files and is only intended for development
# It assumes the ui-frontend folder is located next to the b2share folder
# In production the ui-frontend files must be served by apache/nginx

from flask import Blueprint, current_app, send_from_directory, render_template
import os.path

blueprint = Blueprint('webui', __name__, url_prefix="",
                      template_folder='../../../../ui-frontend/app',
                      static_url_path='',
                      static_folder='static/ui-frontend/app')


@blueprint.route('/', methods=['GET'])
def serve_index():
    print "serving index"
    return render_template("index.html")

@blueprint.route('/bower_components/<path:path>', methods=['GET'])
def serve_any_file_bower(path):
    return serve_any_file('bower_components', path)

@blueprint.route('/css/<path:path>', methods=['GET'])
def serve_any_file_css(path):
    return serve_any_file('css', path)

@blueprint.route('/img/<path:path>', methods=['GET'])
def serve_any_file_img(path):
    return serve_any_file('img', path)

@blueprint.route('/js/<path:path>', methods=['GET'])
def serve_any_file_js(path):
    return serve_any_file('js', path)

@blueprint.route('/layout/<path:path>', methods=['GET'])
def serve_any_file_layout(path):
    return serve_any_file('layout', path)

def serve_any_file(prefix, path):
    assets_dir = current_app.config['ASSETS_LOAD_PATH'][0]
    dir = os.path.join(assets_dir, 'ui-frontend/app', prefix)
    return send_from_directory(dir, path)
