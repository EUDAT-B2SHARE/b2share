# -*- coding: utf-8 -*-
#
# This file is part of EUDAT B2Share.
# Copyright (C) 2017 CERN, University of Tübingen.
#
# B2Share is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# B2Share is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with B2Share; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""B2Share record input loaders."""

from b2share.modules.deposit.loaders import (
    IMMUTABLE_PATHS as DEPOSIT_IMMUTABLE_PATHS,
    check_patch_input_loader
)


IMMUTABLE_PATHS = DEPOSIT_IMMUTABLE_PATHS.union({
    # additional fields immutable for a published record
    '/publication_state',
    '/external_pids',
})

def record_patch_input_loader(record=None):
    return check_patch_input_loader(record, IMMUTABLE_PATHS)
