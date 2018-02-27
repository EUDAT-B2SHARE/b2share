# -*- coding: utf-8 -*-
# This file is part of EUDAT B2Share.
# Copyright (C) 2015 CERN.
#
# Invenio is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

r"""EUDAT B2Share Digital Repository.

B2SHARE is based on the Invenio framework. It uses multiple Invenio **modules**
enabling the storage and processing and of its data.
For a complete list of Invenio modules used by B2SHARE see the
**requirements.txt** file.

As an Invenio application, B2SHARE uses Flask to handle HTTP requests. A
B2SHARE service is initialized by the function :func:`~.factory.create_app`.
This function creates the Flask application and loads all B2SHARE and Invenio
modules.

"""

from .version import __version__


__all__ = ("__version__",)
