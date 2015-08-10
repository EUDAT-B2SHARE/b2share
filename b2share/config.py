from invenio.base.config import PACKAGES as _PACKAGES


PACKAGES = [
    "b2share.modules.*",
    "b2share.base"
] + _PACKAGES


# DEPOSIT_TYPES = [
#     'invenio_demosite.modules.deposit.workflows.article.article',
# ]
