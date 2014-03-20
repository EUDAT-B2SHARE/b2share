# -*- coding: utf-8 -*-

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

"""Utility functions for b2share"""
from invenio.search_engine import perform_request_search
from invenio.bibformat_engine import BibFormatObject
from invenio.bibformat_elements import bfe_authors, bfe_title, bfe_abstract, bfe_creation_date
	

# class MockRequest:
#     str = ""
#     args = {}
#     unparsed_uri=""
#     def write(self, s):
#         self.str += s
#     def send_http_header(self):
#         pass

# req = MockRequest()
# from invenio.search_engine import perform_request_search
# res = perform_request_search(req=req, of="id")

def get_latest_deposits():
	NUMBER_OF_RECORDS = 4;

	ids = perform_request_search(of="id", rg=NUMBER_OF_RECORDS, sf="005", so="a")
	limit_ids = ids[:NUMBER_OF_RECORDS]
	bfo_list = [BibFormatObject(id) for id in limit_ids]
	recs = [{
		"id": bfo.recID,
		"date": bfe_creation_date.format_element(bfo),
		"author": bfe_authors.format_element(bfo, "1"),
		"title": bfe_title.format_element(bfo),
		"description": bfe_abstract.format_element(bfo, 
			prefix_en="", prefix_fr="", suffix_en="", suffix_fr="",	
			limit="", max_chars="72", extension_en="...", extension_fr="..."),
		"category": bfo.field("980__a"), 
	} for bfo in bfo_list]
	return recs
