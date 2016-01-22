# -*- coding: utf-8 -*-
#
# This file is part of EUDAT B2Share.
# Copyright (C) 2016 University of Tuebingen, CERN.
# Copyright (C) 2015 University of Tuebingen.
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

"""B2SHARE"""

from __future__ import absolute_import

from datetime import datetime

schema_basic = {
    '$schema': "http://json-schema.org/draft-04/schema#",
    "id": "http://b2share.eudat.eu/schemas/0",
    "title": "B2SHARE Basic Schema",
    "description": """This is the blueprint of the metadata block
                      that each B2SHARE record must have""",
    "type": "object",
    "properties": {
        "title": {
            "title": "Title",
            "description": "The main title of the record.",
            "type": "string",
        },
        # "description": {
        #     "title": "Description",
        #     "description": "The record abstract.",
        #     "type": "string",
        # },
        "creator": {
            "title": "Author",
            "description": "The record author(s).",
            "type": "array",
            "items": {"type": "string"},
            "uniqueItems": True,
        },
        'keywords': {
            'title': 'Keywords',
            'description': 'Keywords...',
            "type": "array",
            "items": {"type": "string"},
            "uniqueItems": True,
        },
        'open_access': {
            'title': 'Open Access',
            'description': 'Indicate whether the resource is open or access is restricted. In case '
                           'of restricted access the uploaded files will not be public, however the'
                           ' metadata will be.',
            'type': 'boolean',
        },
        'licence': {
            'title': 'Licence',
            'description': 'Specify the license under which this data set is available to the users'
                           ' (e.g. GPL, Apache v2 or Commercial). Please use the License Selector '
                           ' for help and additional information.',
            'type': 'string', # licence chooser plugin here ...
        },
        'embargo_date': {
            'title': 'Embargo Date',
            'description': 'Date that the embargo will expire.',
            'type': 'string',
            'format': 'date-time',
            'default': datetime.now(),
        },
        'contact_email': {
            'title': 'Contact Email',
            'description': 'The email of the contact person for this record.',
            'type': 'string',
            'format': 'email',
        },
        'discipline': {
            'title': 'Discipline',
            'description': 'Scientific discipline...',
            'type': 'string', #  with plugin
        },

        'contributor': {
            'title': 'Contributor',
            'description': 'Contributor...',
            "type": "array",
            "items": {"type": "string"},
            "uniqueItems": True,
        },
        'resource_type': {
            'title': 'Resource Type',
            'description': 'Resource Type...',
            "type": "array",
            "items": {
                'type': 'string',
                'enum': ['Text', 'Image', 'Video', 'Audio', 'Time-Series', 'Other'],
            },
            "uniqueItems": True,
        },
        'version': {
            'title': 'Version',
            'description': 'Version...',
            'type': 'string',
        },
        'language': {
            'title': 'Language',
            'description': 'Language...',
            "type": "string", # plugin
        },
        # 'alternate_identifier' to be moved into relations
    },
    "required": ["title", "description", "open_access"],
    "additionalProperties": False,
    "b2share": {
        "plugins": {
            'licence': 'licence_chooser',
            'discipline': 'discipline_chooser',
            'language': 'language_chooser',
        },
        "mapping": {
            "oai_dc": {
                "title": "dc.title",
                "description": "dc.description",
                "creator": "dc.creator",
                "subject": "dc.subject",
            },
            "marcxml": {
            },
        }
    },
}

schema_bbmri = {
    '$schema': "http://json-schema.org/draft-04/schema#",
    "title": "B2SHARE BBMRI Schema",
    "description": """This is the blueprint of the metadata block
                      specific for the BBMRI community""",
    "type": "object",
    "properties": {
        "study_id": {
            'title': 'Study ID',
            'description': 'The unique ID or acronym for the study',
            'type': 'string',
        },
        'study_design': {
            'title': 'Study design',
            'description': 'The type of study. Can be one or several of the following values.',
            'type': 'array',
            'items': {
                'type': 'string',
                'enum': ['Case-control', 'Cohort', 'Cross-sectional', 'Longitudinal',
                         'Twin-study', 'Quality control', 'Population-based', 'Other'],
            },
        },
        'sex': {
            'title': 'Sex',
            'description': 'The sex of the study participants. Can be several of the following '
                           'values: Female, Male, Other',
            'type': 'array',
            'items': {
                'type': 'string',
                'enum': ['Female', 'Male', 'Other'],
            }
        },
    },
    "additionalProperties": False,
}


schema_clarin = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "title": "B2SHARE CLARIN Schema",
    "description": """This is the blueprint of the metadata block
                      specific for the CLARIN community""",
    "type": "object",
    "properties": {
        'language_code': {
            'title': 'Language Code',
            'description': 'This element can be used to add an ISO language code from '
                           'ISO-639-3 to uniquely identify the language a document '
                           'is written in',
            "type": "string",
            "default": "eng"
        },
        "region": {
            'title': 'Country/Region',
            'description': 'This element allows users to specify a country and/or '
                           'a region to allow depositors to specify where the language '
                           'the document is in is spoken',
            "type": "string",
        },
        "resource_type": {
            'title': 'Resource Type',
            'description': 'This element allows the depositor to specify the type '
                           'of the resource (Text, Audio, Video, Time-Series, Photo, etc.)',
            'type': "array",
            'items': {
                'type': 'string',
                'enum': ['Text', 'Image', 'Video', 'Audio', 'Time-Series', 'Other'],
            }
        },
        "project_name": {
            'title': 'Project Name',
            'description': 'This element allows the depositor to specify the projects '
                           'which were at the source of the creation of the resource',
            'type': "string",
        },
        "quality": {
            'title': 'Quality',
            'description': 'This element allows depositors to indicate the quality of '
                           'the resource allowing potential users to immediately see '
                           'whether the resource is of use for them.',
            'type': "string",
        }
    },
    "required": ["language", "resource_type"],
    "additionalProperties": False,
    "b2share": {
        "plugins": {
            'language_code': 'language_chooser',
        },
        "overwrite": {
            "language_code": {
                "http://b2share.eudat.eu/schemas/B2SHARE+Basic+Optional+Schema": [
                    "language"
                ]
            },
            "resource_type": {
                "http://b2share.eudat.eu/schemas/B2SHARE+Basic+Optional+Schema": [
                    "resource_type"
                ]
            },
        }
    },
}
