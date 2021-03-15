#!/usr/bin/env bash
# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 EUDAT.
#
# B2SHARE is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    CREATE ROLE b2share WITH LOGIN PASSWORD 'b2share';
    ALTER ROLE b2share CREATEDB;
    \du;
EOSQL
