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

