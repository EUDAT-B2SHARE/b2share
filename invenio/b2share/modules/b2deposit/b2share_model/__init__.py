## This file is part of B2SHARE.
## Copyright (C) 2013 EPCC, The University of Edinburgh.
##
## B2SHARE is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## B2SHARE is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with B2SHARE; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

import metadata
import pkgutil

class MetadataClasses:
    domains = None
    def load(self):
        # need to do this lazily due to config settings needing flask.current_app
        from model import _create_metadata_class, SubmissionMetadata
        from flask import current_app
        configured_domains = None

        CFG_B2SHARE_DOMAINS = current_app.config.get('CFG_B2SHARE_DOMAINS')
        if CFG_B2SHARE_DOMAINS:
            configured_domains = [d.strip().lower() for d in
                                  CFG_B2SHARE_DOMAINS.split(',')]

        domains = {SubmissionMetadata.domain.lower(): SubmissionMetadata}
        pck = metadata
        prefix = pck.__name__ + '.'
        for imp, modname, ispkg in pkgutil.iter_modules(pck.__path__, prefix):
            # not sure what fromlist does...
            mod = __import__(modname, fromlist="dummy")
            if hasattr(mod, 'domain'):
                domain_name = mod.domain.lower()
                if not configured_domains or domain_name in configured_domains:
                    domains[domain_name] = _create_metadata_class(mod)
        MetadataClasses.domains = domains

    def __call__(self):
        if not MetadataClasses.domains:
            self.load()
        return MetadataClasses.domains

metadata_classes = MetadataClasses()
