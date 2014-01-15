## This file is part of SimpleStore.
## Copyright (C) 2013 EPCC, The University of Edinburgh.
##
## SimpleStore is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## SimpleStore is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with SimpleStore; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

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
    open_access = db.Column(db.Boolean(), default=True)

    licence = db.Column(db.String(128))  # note we set licences in __init__
    publisher = db.Column(db.String(128))
    publication_date = db.Column('publication_year', db.Date(),
                                 default=date.today())
    tags = db.Column(db.String(256))  # split on ,

    # optional
    contributors = db.Column(db.String(256))  # split on ;
    #language = db.Column(db.Enum(*babel.core.LOCALE_ALIASES.keys()))
    resource_type = db.Column(db.String(256))  # XXX should be extracted to a separate class
    alternate_identifier = db.Column(db.String(256))
    version = db.Column(db.String(128))

    basic_fields = ['title', 'description', 'creator', 'open_access',
                    'licence', 'publisher', 'publication_date', 'tags']
    optional_fields = ['contributors', 'resource_type',
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
        self.field_args['title'] = {
            'description':
            'This is the title of the uploaded resource - a name that ' +\
            'indicates the content to be expected.'}
        self.field_args['description'] = {
            'description':
            'This is a more elaborate description of the resource without ' +\
            'semantic restrictions. It should focus on a description of ' +\
            'content making it easy for others to find it and to ' +\
            'interpret its relevence quickly.'
        }
        self.field_args['publisher'] = {
            'description':
            'Here should be stored the site that will host the BE2Share ' +\
            'container, so that in case of access problems, people can ' +\
            'be contacted. This element can be created automatically ' +\
            'dependent on the centre.'
        }                         
        self.field_args['publication_date'] = {
            'description':
            'This is the date that the resource was uploaded and thus ' +\
            'being available broadly. Also this date can be extracted ' +\
            'automatically.'
        }
        self.field_args['version'] = {
            'description':
            'This element can be added by the depositor to denote whether ' +\
            'there are new versions etc.'
        }              
        self.field_args['licence'] = {
            'data_provide': 'typeahead',
            'data_source': '["GPL","Apache v2","Commercial", "Other"]',
            'description': 'It might be the case that people need to sign ' +\
                           'a licence agreement to access the data. This ' +\
                           'element offers a pointer to the licence ' +\
                           'agreement or code of conduct.'
                           }
        self.field_args['tags'] = {
            'description':
            'This is an element where people can add a comma separated list ' +\
            'of tags (keywords) that ' +\
            'may characterize the content. In a later phase users should be ' +\
            'able to also add tags. Multiple values are allowed in this tag.'}
        self.field_args['open_access'] = {
            'description':
            'This element indicates whether the resource is open or access ' +\
            'is restricted. In case of restricted access the uploaded files ' +\
            'will not be public, however the metadata will be'}
        self.field_args['contributors'] = {
            'description':
            'This element contains a semicolon separated list of ' +\
            'contributors, e.g. further authors. Here people can mention all ' +\
            'other persons that were relevant in the creation of the resource.'}
#        self.field_args['language'] = {
#            'description': 
#           'This element specifies the name of the language the document ' +\
#            'is written in.',
#	    }
        self.field_args['resource_type'] = {
            'description': 
            'This element allows the depositor to specify the type of the ' +\
            'resource, e.g. written report, audio or video.'}
        self.field_args['alternate_identifier'] = {
            'description': 
            'This element allows the depositor to add any kind of other ' +\
            'reference such as a URN, URI or an ISBN number.'}
        self.field_args['creator'] = {           
            'description': 'Either the person who created the resource or ' +\
                           'the person who uploaded the resource.'}

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
        if 'default' in f:
            args['field_args'][f['name']]['default'] = f.get('default')

    return type(clsname, (SubmissionMetadata,), args)
