import os
import flask
import flask.ext.assets
import flask.ext.cache
from myext import CollectionExtension, LangExtension

app = flask.Flask(__name__)
app.debug = True
app.jinja_env.add_extension(CollectionExtension)
app.jinja_env.add_extension(LangExtension)
app.jinja_env.add_extension('jinja2.ext.do')

assets = flask.ext.assets.Environment(app)
assets.debug = True
def _jinja2_new_bundle(tag, collection, name=None):
	if len(collection):
		return flask.ext.assets.Bundle(output="%s/%s-%s.%s" %
					  (tag, 'invenio' if name is None else name,
					   hash('|'.join(collection)), tag), *collection)

app.jinja_env.extend(new_bundle=_jinja2_new_bundle, default_bundle_name='90-invenio')

app.jinja_env.globals['current_user'] = { "is_guest":True }
app.jinja_env.globals['is_language_rtl'] = lambda x: False
app.jinja_env.globals['alternate_urls'] = {}
app.jinja_env.globals['get_css_bundle'] = app.jinja_env.get_css_bundle
app.jinja_env.globals['get_js_bundle'] = app.jinja_env.get_js_bundle

app.jinja_env.globals['collection'] = {
	'is_restricted': True,
	'name': "Collection",
	'search_within': [["author", "Author"], ["title", "Title"]]
}

def my_url_for(endpoint, **values):
	try:
		return app.jinja_env.url_for(endpoint, **values)
	except:
		return endpoint
app.jinja_env.globals['url_for'] = my_url_for
app.jinja_env.globals['_'] = lambda x: x
app.config['breadcrumbs_map'] = {}
app.config['menubuilder_map'] = {'main':{'children':{}}}
app.config['CFG_WEBSEARCH_MAX_RECORDS_IN_GROUPS'] = 200

cache = flask.ext.cache.Cache(app)

class CustomRequestGlobals(object):
	def __init__(self):
		self.ln = ''
app.app_ctx_globals_class = CustomRequestGlobals

@app.template_filter('invenio_format_date')
def invenio_format_date(s):
    return s

@app.route('/')
def site_root():
	return flask.render_template('websearch_index.html')

@app.route('/css/<filename>')
def serve_css(filename):
	with open(os.getcwd()+"/../var/www/css/" + filename) as file:
		return flask.Response(response=file.read(), status=200, mimetype="text/css")

@app.route('/js/<filename>')
def serve_js(filename):
	with open(os.getcwd()+"/../var/www/js/" + filename) as file:
		return flask.Response(response=file.read(), status=200, mimetype="application/javascript")

@app.route('/img/<filename>')
def serve_img(filename):
	with open(os.getcwd()+"/../var/www/img/" + filename) as file:
		return flask.Response(response=file.read(), status=200, mimetype="image/jpeg")




if __name__ == '__main__':
	app.run()
