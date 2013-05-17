from uuid import uuid4

from invenio.sqlalchemyutils import db

import babel


class Submission(db.Model):
    __tablename__ = 'submission'
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.CHAR(32), unique=True, nullable=False)
    content = db.Column(db.LargeBinary())
    # metadata name is reserved, so using md
    md = db.relationship('SubmissionMetadata', backref='submission', uselist=False)

    def __init__(self, uuid=None, content=None):
        self.uuid = uuid if uuid is not None else uuid4().hex
        self.content = content

    def __repr__(self):
        return '<Submission %s>' % self.uuid


class SubmissionMetadata(db.Model):
    """DataCite-based metadata class. Format description is here:
    http://schema.datacite.org/meta/kernel-2.2/doc/DataCite-MetadataKernel_v2.2.pdf
    """
    __tablename__ = 'submission_metadata'
    submission_id = db.Column(db.Integer, db.ForeignKey('submission.id'))

    # id seems to be needed to maintain link to parent submission
    id = db.Column(db.Integer, primary_key=True)
    creator = db.Column(db.String(128))
    title = db.Column(db.String(256))
    publisher = db.Column(db.String(128))
    publication_year = db.Column(db.Date())

    def basicFieldIter(self):
        #why won't submission_id work?
        for f in ['creator', 'title', 'publisher',
                  'publication_year']:
            yield f

    # optional
    subject = db.Column(db.String(256))
    contributor = db.Column(db.String(256))
    date = db.Column(db.Date())
    language = db.Column(db.Enum(*babel.core.LOCALE_ALIASES.keys()))
    resource_type = db.Column(db.String(256))  # XXX should be extracted to a separate class
    alternate_identifier = db.Column(db.String(256))
    related_identifier = db.Column(db.String(256))
    size = db.Column(db.String(256))
    format = db.Column(db.String(256))  # file extension or MIME
    version = db.Column(db.Integer)
    rights = db.Column(db.String(256))  # not sure how to serialize rights
    description = db.Column(db.String(1024))

    def optionalFieldIter(self):
        for f in ['subject', 'contributor', 'date', 'language',
                  'resource_type', 'alternate_identifier',
                  'related_identifier', 'size', 'format',
                  'version', 'rights', 'description']:
            yield f

    # administrative metadata
    # XXX are we going to use them?
    # last_metadata_update = hook?
    # metadata_version_number = schema migration version?

    # using joined table inheritance for the specific domains
    submission_type = db.Column(db.String(50))
    __mapper_args__ = {
        'polymorphic_identity': 'generic',
        'polymorphic_on': submission_type
    }

    def __repr__(self):
        return '<SubmissionMetadata %s>' % self.id

    def __init__(self, creator="", title="", publisher="", publication_year=None):
        self.creator = creator
        self.title = title
        self.publisher = publisher
        self.publication_year = publication_year


class LinguisticsMetadata(SubmissionMetadata):
    id = db.Column(db.Integer, db.ForeignKey('submission_metadata.id'),
                   primary_key=True)

    phrase_popularity = db.Column(db.String(256))  # a stub field

    def basicFieldIter(self):
        for s in SubmissionMetadata.basicFieldIter(self):
            yield s
        yield 'phrase_popularity'

    __mapper_args__ = {
        'polymorphic_identity': 'linguistics',
    }

    def __repr__(self):
        return '<LinguisticsMetadata %s>' % self.id

    def __init__(self, phrase_popularity=""):
        SubmissionMetadata.__init__(self)  # need to add args
        self.phrase_popularity = phrase_popularity
