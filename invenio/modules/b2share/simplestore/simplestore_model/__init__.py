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
