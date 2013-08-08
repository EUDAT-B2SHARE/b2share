from  invenio.simplestore_model import metadata
from model import _create_metadata_class, SubmissionMetadata
import pkgutil

# might well be a better way to do this
metadata_classes = {SubmissionMetadata.domain.lower(): SubmissionMetadata}
try:
    from invenio.config import CFG_SIMPLESTORE_DOMAINS
    configured_domains = [d.strip().lower() for d in
                          CFG_SIMPLESTORE_DOMAINS.split(',')]
except ImportError:
    configured_domains = None


pck = metadata
prefix = pck.__name__ + '.'
for imp, modname, ispkg in pkgutil.iter_modules(pck.__path__, prefix):
    # not sure what fromlist does...
    mod = __import__(modname, fromlist="dummy")
    if hasattr(mod, 'domain'):
        domain_name = mod.domain.lower()
        if not configured_domains or domain_name in configured_domains:
            metadata_classes[domain_name] = _create_metadata_class(mod)
