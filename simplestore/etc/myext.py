from operator import itemgetter
from jinja2 import nodes
from jinja2.ext import Extension

ENV_PREFIX = '_collected_'

def prepare_tag_bundle(cls, tag):
    def get_bundle(key=None, iterate=False):

        def _get_data_by_key(data_, key_):
            return map(itemgetter(1), filter(lambda (k, v): k == key_, data_))

        data = getattr(cls.environment, ENV_PREFIX+tag)

        if iterate:
            bundles = sorted(set(map(itemgetter(0), data)))
            print "%s bundles are: " % tag, bundles
            def _generate_bundles():
                for bundle in bundles:
                    cls._reset(tag, bundle)
                    bundle_list = cls.environment.new_bundle(tag,
                                                     _get_data_by_key(data, bundle),
                                                     bundle)
                    print "%s bundle: " % tag, bundle, bundle_list
                    for b in bundle_list:
                        yield b
            return _generate_bundles()
        else:
            if key is not None:
                data = _get_data_by_key(data, key)
            else:
                bundles = sorted(set(map(itemgetter(0), data)))
                data = [f for bundle in bundles
                        for f in _get_data_by_key(data, bundle)]

            cls._reset(tag, key)
            return cls.environment.new_bundle(tag, data, key)
    return get_bundle

class CollectionExtension(Extension):
    tags = set(['css', 'js'])

    def __init__(self, environment):
        super(CollectionExtension, self).__init__(environment)
        ext = dict(('get_%s_bundle' % tag, prepare_tag_bundle(self, tag))
                   for tag in self.tags)
        environment.extend(
            default_bundle_name='10-default',
            use_bundle=True,
            collection_templates=dict((tag, lambda x: x) for tag in self.tags),
            new_bundle=lambda tag, collection, name: collection,
            **ext)
        for tag in self.tags:
            self._reset(tag)

    def _reset(self, tag, key=None):
        """
        Empty list of used scripts.
        """
        if key is None:
            setattr(self.environment, ENV_PREFIX+tag, [])
        else:
            data = filter(lambda (k, v): k != key,
                          getattr(self.environment, ENV_PREFIX+tag))
            setattr(self.environment, ENV_PREFIX+tag, data)

    def _update(self, tag, value, key, caller=None):
        """
        Update list of used scripts.
        """
        try:
            values = getattr(self.environment, ENV_PREFIX+tag)
            values.append((key, value))
        except:
            values = [(key, value)]

        setattr(self.environment, ENV_PREFIX+tag, values)
        return ''

    def parse(self, parser):
        """
        Parse Jinja statement tag defined in `self.tags` (default: css, js).

        This accually tries to build corresponding html script tag
        or collect script file name in jinja2 environment variable.
        If you use bundles it is important to call ``get_css_bundle``
        or ``get_js_bundle`` in template after all occurrences of
        script tags (e.g. {% css ... %}, {% js ...%}).
        """
        tag = parser.stream.current.value
        lineno = next(parser.stream).lineno

        default_bundle_name = u"%s" % (self.environment.default_bundle_name)
        default_bundle_name.encode('utf-8')
        bundle_name = nodes.Const(default_bundle_name)

        #parse filename
        if parser.stream.current.type != 'block_end':
            value = parser.parse_expression()
            # get first optional argument: bundle_name
            if parser.stream.skip_if('comma'):
                bundle_name = parser.parse_expression()
                if isinstance(bundle_name, nodes.Name):
                    bundle_name = nodes.Name(bundle_name.name, 'load')
        else:
            value = parser.parse_tuple()

        args = [nodes.Const(tag), value, bundle_name]

        # Return html tag with link to corresponding script file.
        if self.environment.use_bundle is False:
            value = value.value
            if callable(self.environment.collection_templates[tag]):
                node = self.environment.collection_templates[tag](value)
            else:
                node = self.environment.collection_templates[tag] % value
            return nodes.Output([nodes.MarkSafeIfAutoescape(nodes.Const(node))])

        # Call :meth:`_update` to collect names of used scripts.
        return nodes.CallBlock(self.call_method('_update', args=args,
                                                lineno=lineno),
                               [], [], '')

class LangExtension(Extension):
    tags = set(['lang'])

    def parse(self, parser):
        lineno = parser.stream.next().lineno

        body = parser.parse_statements(['name:endlang'], drop_needle=True)

        return nodes.CallBlock(self.call_method('_lang'),
                               [], [], body).set_lineno(lineno)

    def _lang(self,  caller):
        return filter_languages('<lang>' + caller() + '</lang>', g.ln)
