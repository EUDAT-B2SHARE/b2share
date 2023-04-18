# -*- coding: utf-8 -*-
#
# This file is part of EUDAT B2Share.
# Copyright (C) 2022 CSC Ltd, EUDAT CDI.
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

"""Utilities for B2SHARE config loader."""

def _check_config_exists(
    app,
    required_config_variables,
    optional_config_variables
    ):
    """."""
    config_complete = True
    for c in required_config_variables:
        if app.config.get(c, None) in ("", [], None):
            app.logger.warning(
                f"REQUIRED config variable {c} has an empty value"
                )
            config_complete = False

    for c in optional_config_variables:
        if app.config.get(c, None) in ("", [], None):
            app.logger.info(
                f"Optional config variable {c} has an empty value"
                )

    return config_complete
