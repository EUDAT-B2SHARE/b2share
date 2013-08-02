from invenio.sqlalchemyutils import db
from datetime import date
import babel


class FieldSet:

    def __init__(self, name, basic_fields=[], optional_fields=[]):
        self.name = name
        self.basic_fields = basic_fields
        self.optional_fields = optional_fields


class SubmissionMetadata(db.Model):
    """DataCite-based metadata class. Format description is here:
    http://schema.datacite.org/meta/kernel-2.2/doc/DataCite-MetadataKernel_v2.2.pdf
    """
    __tablename__ = 'submission_metadata'
    domain = 'Generic'
    icon = 'icon-question-sign'
    kind = 'domain'
    field_args = {}

    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text(), nullable=False)
    creator = db.Column(db.String(128))
    title = db.Column(db.String(256), nullable=False)
    open_access = db.Column(db.Boolean())

    licence = db.Column(db.String(128))  # note we set licences in __init__
    publisher = db.Column(db.String(128))
    publication_date = db.Column('publication_year', db.Date(),
                                 default=date.today())
    tags = db.Column(db.String(256))  # split on ,

    # optional
    contributors = db.Column(db.String(256))  # split on ;
    language = db.Column(db.Enum(*babel.core.LOCALE_ALIASES.keys()))
    resource_type = db.Column(db.String(256))  # XXX should be extracted to a separate class
    alternate_identifier = db.Column(db.String(256))
    version = db.Column(db.String(128))

    basic_fields = ['title', 'description', 'creator', 'open_access',
                    'licence', 'publisher', 'publication_date', 'tags']
    optional_fields = ['contributors', 'language', 'resource_type',
                       'alternate_identifier', 'version']

    # using joined table inheritance for the specific domains
    submission_type = db.Column(db.String(50))
    __mapper_args__ = {
        'polymorphic_identity': 'generic',
        'polymorphic_on': submission_type
    }

    def __repr__(self):
        return '<SubmissionMetadata %s>' % self.id

    def __init__(self):
        self.fieldsets = [(FieldSet("Generic",
                                    basic_fields=self.basic_fields,
                                    optional_fields=self.optional_fields))]
        self.field_args['licence'] = {
            'data_provide': 'typeahead',
            'data_source': '["GPL","Apache v2","Commercial", "Other"]'}
        self.field_args['tags'] = {
            'description':
            'Comma separated list of keywords associated with item'}
        self.field_args['open_access'] = {
            'description': 'Open Access items may be downloaded by anyone'}
        self.field_args['contributors'] = {
            'description':
            'Semicolon separated list of contributors e.g. further authors'}
        self.field_args['language'] = {
            'description': 'Principal language of submission'}
        self.field_args['resource_type'] = {
            'description': 'e.g. written report, audio or video'}
        self.field_args['alternate_identifier'] = {
            'description': 'e.g. ISBN number'}


def _create_metadata_class(cfg):
    """Creates domain classes that map form fields to databases plus some other
    details."""

    if not hasattr(cfg, 'fields'):
        cfg.fields = []

    # TODO: this can be done in a simpler and clearer way now
    def basic_field_iter():

        #Normal field if extra is false or not set
        for f in cfg.fields:
            try:
                if not f['extra']:
                    yield f['name']
            except KeyError:
                yield f['name']

    def optional_field_iter():

        for f in cfg.fields:
            try:
                if f['extra']:
                    yield f['name']
            except KeyError:
                pass

    def __init__(self):
        super(type(self), self).__init__()
        self.fieldsets.append(FieldSet(
            cfg.domain,
            basic_fields=list(basic_field_iter()),
            optional_fields=list(optional_field_iter())))

    clsname = cfg.domain + "Metadata"

    args = {'__init__': __init__,
            '__tablename__': cfg.table_name,
            '__mapper_args__': {'polymorphic_identity': cfg.table_name},
            'id': db.Column(
                db.Integer, db.ForeignKey('submission_metadata.id'),
                primary_key=True),
            'field_args': {}}

    #The following function and call just add all external attrs manually
    def is_external_attr(n):

        # don't like this bit; problem is we don't want to include the
        # db import and I don't know how to exclude them except via name
        if n in ['db', 'fields']:
            return False

        return not n.startswith('__')

    for attr in (filter(is_external_attr, dir(cfg))):
        args[attr] = getattr(cfg, attr)

    # field args lets us control some aspects of the field
    # including label, validators and decimal places
    for f in cfg.fields:
        nullable = not f.get('required', False)
        args[f['name']] = db.Column(f['col_type'], nullable=nullable)
        # Doesn't seem pythonic, but show me a better way
        args['field_args'][f['name']] = {}
        if 'display_text' in f:
            args['field_args'][f['name']]['label'] = f.get('display_text')
        if 'description' in f:
            args['field_args'][f['name']]['description'] = f.get('description')
        if 'data_provide' in f:
            args['field_args'][f['name']]['data_provide'] = f.get('data_provide')
        if 'data_source' in f:
            args['field_args'][f['name']]['data_source'] = f.get('data_source')

    return type(clsname, (SubmissionMetadata,), args)
