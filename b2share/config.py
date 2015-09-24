from invenio_base.config import PACKAGES as _PACKAGES


PACKAGES = [
    "b2share.modules.*",
    "b2share.base",
    "invenio_oaiharvester"
] + _PACKAGES

PACKAGES_EXCLUDE = [
    "b2share.modules.b2deposit"
    'invenio_annotations',
    'invenio_archiver',
    'invenio_communities',
    'invenio_linkbacks',
    'invenio_multimedia',
    'invenio_pages',
    'invenio_deposit',
]

# all invenio modules because exclude does not accept wildcards
invenio_modules = [
    "invenio_collections",
    'invenio_annotations',
    'invenio_documentation',
    'invenio_messages',
    'invenio_records',
    'invenio_authorprofiles',
    'invenio_editor',
    'invenio_oaiharvester',
    'invenio_scheduler',
    'invenio_authors',
    'invenio_formatter',
    'invenio_oairepository'
    'invenio_tags',
    'invenio_cloudconnector',
    'invenio_groups',
    'invenio_pages',
    'invenio_uploader',
    'invenio_comments',
    'invenio_knowledge',
    'invenio_pidstore',
    'invenio_communities',
    'invenio_linkbacks',
    'invenio_previewer',
    'invenio_access',
    'invenio_accounts',
    'invenio_deposit',
    'invenio_oauth2server',
    'invenio_oauthclient',
    'invenio_search',
    'invenio_workflows',
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

