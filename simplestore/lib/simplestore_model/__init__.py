from  invenio.simplestore_model import metadata
from model import _create_metadata_class, SubmissionMetadata
import pkgutil

# might well be a better way to do this
metadata_classes = {SubmissionMetadata.domain.lower(): SubmissionMetadata}

pck = metadata
prefix = pck.__name__ + '.'
for imp, modname, ispkg in pkgutil.iter_modules(pck.__path__, prefix):
    # not sure what fromlist does...
    mod = __import__(modname, fromlist="dummy")
    metadata_classes[mod.domain.lower()] = _create_metadata_class(mod)
