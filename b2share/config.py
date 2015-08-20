from invenio.base.config import PACKAGES as _PACKAGES


PACKAGES = [
    "b2share.modules.*",
    "b2share.base"
] + _PACKAGES


PACKAGES_EXCLUDE = [
    'invenio.modules.annotations',
    'invenio.modules.archiver',
    'invenio.modules.communities',
    'invenio.modules.linkbacks',
    'invenio.modules.multimedia',
    'invenio.modules.pages',
    'invenio.modules.deposit',
]

# all invenio modules because exclude does not accept wildcards
invenio_modules = [
    'invenio.invenio.modules.annotations',
    'invenio.invenio.modules.documentation',
    'invenio.invenio.modules.messages',
    'invenio.invenio.modules.records',
    'invenio.invenio.modules.authorprofiles',
    'invenio.invenio.modules.editor',
    'invenio.invenio.modules.oaiharvester',
    'invenio.invenio.modules.scheduler',
    'invenio.invenio.modules.authors',
    'invenio.invenio.modules.formatter',
    'invenio.invenio.modules.oairepository'
    'invenio.invenio.modules.tags',
    'invenio.invenio.modules.cloudconnector',
    'invenio.invenio.modules.groups',
    'invenio.invenio.modules.pages',
    'invenio.invenio.modules.uploader',
    'invenio.invenio.modules.comments',
    'invenio.invenio.modules.knowledge',
    'invenio.invenio.modules.pidstore',
    'invenio.invenio.modules.communities',
    'invenio.invenio.modules.linkbacks',
    'invenio.invenio.modules.previewer',
    'invenio.invenio.modules.access',
    'invenio.invenio.modules.accounts',
    'invenio.invenio.modules.deposit',
    'invenio.invenio.modules.oauth2server',
    'invenio.invenio.modules.oauthclient',
    'invenio.invenio.modules.search',
    'invenio.invenio.modules.workflows',
]

# Exclude all Invenio views
PACKAGES_VIEWS_EXCLUDE = invenio_modules
# Exclude all Invenio REST APIs
PACKAGES_RESTFUL_EXCLUDE = invenio_modules


from b2share.modules.oauthclient import unity

OAUTHCLIENT_REMOTE_APPS = dict(
    unity=unity.REMOTE_APP,
)

UNITY_APP_CREDENTIALS = dict(
    # will only work on development configurations
    consumer_key= "b2share",
    consumer_secret= "b2share8juelich",
)

# DEPOSIT_TYPES = [
#     'invenio_demosite.modules.deposit.workflows.article.article',
# ]

