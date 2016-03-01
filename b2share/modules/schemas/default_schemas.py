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


from __future__ import absolute_import

from datetime import datetime


record_json_template = {
    "id": "ee28c046-e533-4434-8850-4a27249792e3",
    "created": "2016-02-23T11:26:34.130676+00:00",
    "updated": "2016-02-23T11:26:34.130681+00:00",
    "version_id": 1,

    "metadata": {
        "$schema": "http://b2share/...",
        "@context": {},

        "owner_id": "2D9932C7-CA95-4560-8B0B-A6289F2F21CC",
        "community_id": "7A6744C4-DA71-4433-A719-931FE972D37C",

        "record_status": "draft",

        # generic, global fields, basically equivalent with DC
        "title": "Interaction and dialogue with ...",
        "creator": [
            "Prof. Dr. Andreas Blütte"
        ],
        "description":  "Prof. Dr. Andreas Blütte's keynote...",
        "open_access": True,

        "files": [
            {
                "file_id": 1,
                "type": "",
                "uri": "http://"
            }
        ],
        "community_specific": {
            # community-specific metadata block
            "B0B4A784-1A71-42E7-BB31-84AF90518332": {
                "project_name": "xxx",
                "region": "xxx",
                "language_code": "xxx",
            },
        },
        "references": [
            {
                "reference_id": 1,
                "type": "article",
                "uri": "http://arxiv.org/abs/1512.00849"
            }
        ],
    }
}


# on PUT with application/json:
# {
#         "title": "Interaction and dialogue with ...",
#         "creator": [
#                "Prof. Dr. Andreas Blütte"
#         ],
#         "description":  "Prof. Dr. Andreas Blütte's keynote...",
# }

# “$schema”: “http://.../api/schemas/<id>#/schema”

# “http://.../api/schemas/<id>” => {
#   id: …
#   links: { self: … }
#   community_id: …
#   block_schema: true,                         # block_schema = true  means that this is a sub-schema (small schema)
#   status: draft                                            # other values: released, deprecated
#   recommended_successor: http://.../api/schemas/<id>       # if the current status is deprecated
#   schema: {
#    <JSON_SCHEMA>
#  }
# }

# GET /api/schemas/schemas?accepted_by=<community_id>&block_schema=false

# GET /api/schemas/schemas?accepted_by=<community_id>&name=particle physics*

#
#
#
#
#
#
#
#
#
#


def make_community_schema(community_id):
    return {
        "title": "B2SHARE Community Schema",
        "description": "This is the schema internally used for validating "
                       "a B2SHARE record's metadata",
        "allOf": [
            {   # fields inserted by the server, programmatically: owner_id, files
                "type": "object",
                "properties": {
                    "owner_id": {
                        "title": "OwnerID",
                        "description": "Record's owner id",
                        "type": "string",
                    },
                    "files": {
                        'type':'array',
                        "items": {
                            "type": "object",
                        },
                        "uniqueItems": True,
                    },
                }
            },
            make_community_schema_for_api_inputs(community_id)
        ],
    }


def make_community_schema_for_api_inputs(community_id):
    return {
        "title": "B2SHARE Community Schema ",
        "description": "This is the schema used by B2SHARE for validating data "
                       "coming from the REST API and going into a record",
        "allOf": [
            {
                "type": "object",
                "properties": {
                    "community_id": {
                        "title": "CommunityID",
                        "description": "The Community id that the record belongs to",
                        'type':'string',
                        'enum':[str(community_id)]
                    },

                    "record_status": {
                        'type': 'string',
                        'enum': ['draft', 'submitted', 'released', 'deleted'],
                    },

                    "community_specific": {
                        'type':'object',
                        "properties": {}, # no required properties
                        # we must programmatically enforce constraints here,
                        # the name of a property indicates the schema to use for its validation
                    },

                    "references": {
                        'type':'array',
                        "items": {
                            "type": "object",
                        },
                        "uniqueItems": True,
                    }
                }
            },
            basic_dc_fields,
        ]
    }

basic_dc_fields = {
    "title": "B2SHARE Basic Block Schema",
    "description": "This is the schema used for validating "
                   "the basic metadata fields of a B2SHARE record",
    "type": "object",
    "properties": {
        "title": {
            "title": "Title",
            "description": "The main title of the record.",
            "type": "string",
        },
        "description": {
            "title": "Description",
            "description": "The record abstract.",
            "type": "string",
        },
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
            'default': str(datetime.now()),
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
        'alternate_identifier': {
            'title': 'Alternate Identifier',
            'description': 'Alternate Identifier...',
            "type": "string"
        },
    },
    "required": ["title", "description", "open_access"],
    "additionalProperties": True,
    "b2share": {
        "recommended": ['creator', 'licence', 'publication_date',
                        'keywords', 'contact_email', 'discipline'],
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

block_schema_bbmri = {
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


block_schema_clarin = {
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

block_schema_clarin2 = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "title": "B2SHARE CLARIN Duplicated Schema",
    "description": """This is the blueprint of the metadata block
                      specific for the CLARIN community, duplicated""",
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
