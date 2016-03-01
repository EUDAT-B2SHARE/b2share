# -*- coding: utf-8 -*-

"""mysite base Invenio configuration."""

from __future__ import absolute_import, print_function

import random

from flask_cli import with_appcontext

from invenio_base.app import create_cli

from .factory import create_app

from invenio_db import db
from b2share.modules.communities.api import Community
from b2share.modules.records.api import Record
from b2share.modules.schemas.api import Schema
from b2share.modules.schemas.default_schemas import make_community_schema
from b2share.modules.schemas.default_schemas import block_schema_bbmri, block_schema_clarin


cli = create_cli(create_app=create_app)


@cli.command()
@with_appcontext
def add_communities():
    add_test_communities()

def add_test_communities():
    for c in test_communities:
        community = Community.create_community(name=c.get('name'),
                                               description=c.get('description'),
                                               logo=c.get('logo'))
        db.session.commit()
        print ("----------- Created community {}".format(community.id))

        for s in c.get('schemas'):
            Schema.create_schema(community_id=community.id, json_schema=s, block_schema=True)
        db.session.commit()

        jsonschema = make_community_schema(community.id)
        schema = Schema.create_schema(community_id=community.id, json_schema=jsonschema, block_schema=False)
        db.session.commit()

        print ("----------- Created community schema {}".format(schema.get_id()))

test_communities = [
    {
        'name': "Eudat",
        'description': "The big Eudat community. Use this community if no other is suited for you",
        'logo': "/img/communities/eudat.png",
        'schemas': []
    },
    {
        'name': "BBMRI",
        'description': "Biomedical Research data",
        'logo': "/img/communities/bbmri.png",
        'schemas': [block_schema_bbmri]
    },
    {
        'name': "CLARIN",
        'description': "The Clarin linguistics community",
        'logo': "/img/communities/clarin.png",
        'schemas': [block_schema_clarin, block_schema_clarin]
    },
    {
        'name': "DRIHM",
        'description': 'Meteorology and climate data.',
        'logo': '/img/communities/drihm.png',
        'schemas': []
    },
    {
        'name': "NRM",
        'description': "Herbarium data.",
        'logo': "/img/communities/nrm.png",
        'schemas': []
    },
    {
        'name': "RDA",
        'description': "Research Data Alliance community.",
        'logo': "/img/communities/rda.png",
        'schemas': []
    },
]


@cli.command()
@with_appcontext
def add_records():
    add_test_records()

def add_test_records():
    for desc in test_record_descriptions:
        md = {'schema_id': "0", 'open_access': True, }
        md.update(desc)
        json = {
            'community_id': random.randint(1, 6),
            'record_status': 'draft',
            "metadata": [md],
            'references': [
                {
                    'id': 1,
                    'type': 'article',
                    'uri': 'http://arxiv.org/abs/1512.00849',
                }
            ],
            'files': [
                {
                    'id': 1,
                    'type': '',
                    'uri': 'http://'
                }
            ],
        }
        record = Record.create(json)
        print ("----------- Created record {}".format(record.get_id()))


test_record_descriptions = [
    {
        'title': "Interaction and dialogue with large-scale textual data: "
                 "Parliamentary speeches of migrants and speeches about migration",
        'creator': ['Prof. Dr. Andreas Blätte'],
        'description': " Prof. Dr. Andreas Blätte's keynote talk at the CLARIN Annual "
                       "Conference 2015. Additional material, including the presented "
                       "3D visualisations, are available via "
                       "https://www.clarin.eu/node/4195#keynote",
    },
    {
        'title': "Simple workflow for conceptual models",
        'creator': ['Schentz'],
        'description': "A workflow for the creation of a conceptual "
                       "model which discouples the discussion process"
                       " from the voting process",
    },
    {
        'title': "Multi-model change of temperature and precipitation "
                 "for mid 21st century over France; SCRATCH2010",
        'creator': ['Christian Pagé'],
        'description': "This is a multi-model graphic showing the relative "
                       "change of temperature and precipitation at the surface "
                       "for France for 2046-2065 compared to the period 1961-1990. "
                       "This is the result of a statistical downscaling applied to "
                       "CMIP3 climate data.",
    },
    {
        'title': "Replication of part of the IFA corpus",
        'creator': ['Nederlandse Taalunie and R.J.J.H. van Son'],
        'description': "The IFA Spoken Language corpus is a free (GPL) database of hand-segmented Dutch speech. It was constructed with off-the-shelf software using speech from 8 speakers in a variety of speaking styles. For a total of 50,000 words (41 minutes/speaker), speech acquisition and preparation took around 3 person-weeks per speaker. Hand segmentation took 1,000 hours of labeling altogether. The asymptotic segmentation speed was about one word, or four boundaries, per minute. An evaluation showed that the Median Absolute Difference of the segment boundaries was 6 ms between labelers, and 4 ms within labelers. Label differences (substitutions, insertions, and deletions) were found in 8% of the segments between labelers and 5% within labelers."
    },
    {
        'title': "Experimental Factor Ontology",
        'creator': ['James Malone'],
        'description': "An ontology of experimental variables used in biomedical experiments, largely at European Bioinformatics Institute to annotate data."
    },
    {
        'title': "SMEAR Hyytiälä",
        'creator': ['Junninen, H ; Lauri, A ; Keronen, P ; Aalto, P ; Hiltunen, V ; Hari, P ; Kulmala, M.'],
        'description': "atmospheric, flux, soil, tree physiological and water quality measurements at SMEAR Hyytiälä research station of the University of Helsinki."
    },
    {
        'title': "Orthography-based dating and localisation of Middle Dutch charters ",
        'creator': ['Dieter Van Uytvanck'],
        'description': "In this study we build models for the localisation and dating of Middle Dutch charters. First, we extract character trigrams and use these to train a machine learner (K Nearest Neighbours) and an author verification algorithm (Linguistic Profiling). Both approaches work quite well, especially for the localisation task. Afterwards, an attempt is made to derive features that capture the orthographic variation between the charters more precisely. These are then used as input for the earlier tested classification algorithms. Again good results (at least as good as using the trigrams) are attained, even though proper nouns were ignored during the feature extraction. We can conclude that the localisation, and to a lesser extent the dating, is feasible. Moreover, the orthographic features we derive from the charters are an efficient basis for such a classification task."
                        "One file (PDF) contains the text of the master thesis, the other file (.tar.gz) contains all the used data sets and analysis scripts."
    },
    {
        'title': "Annotated Route Description",
        'creator': ['Peter Wittenburg', 'Kita Sotaro'],
        'description': "This file set existing of a video stream, an audio stream and a multimodal annotation file is a frequently used as show case of how to do complex multimodal annotations with the well-known ELAN tool (http://tla.mpi.nl/tools/tla-tools/elan/download/)."
    },
    {
        'title': "SMEAR Kumpula 2005-2014; 22-01-2014",
        'creator': ['atm-data@helsinki.fi Junninen, H; Lauri, A; Keronen, P; Aalto, P; Hiltunen, V; Hari, P; Kulmala, M. Smart-SMEAR: on-line data exploration and visualization tool for SMEAR stations. BOREAL ENVIRONMENT RESEARCH (BER) Vol 14, Issue 4, pp.447-457 ; Junninen, H ; Lauri, A ; Keronen, P ; Aalto, P ; Hiltunen, V ; Hari, P ; Kulmala, M.'],
        'description': "Helsinki Smear station"
                        "lat 60° 12.173' lon 24° 57.663'"
                        "https://wiki.helsinki.fi/display/SMEAR/Helsinki+database"
                        "http://www.atm.helsinki.fi/SMEAR/"

    },
    {
        'title': "SMEAR Hyytiälä -2009; 23-01-2014",
        'creator': ['atm-data@helsinki.fi Junninen, H; Lauri, A; Keronen, P; Aalto, P; Hiltunen, V; Hari, P; Kulmala, M. Smart-SMEAR: on-line data exploration and visualization tool for SMEAR stations. BOREAL ENVIRONMENT RESEARCH (BER) Vol 14, Issue 4, pp.447-457 ; Junninen, H ; Lauri, A ; Keronen, P ; Aalto, P ; Hiltunen, V ; Hari, P ; Kulmala, M. ; Junninen, H ; Lauri, A ; Keronen, P ; Aalto, P ; Hiltunen, V ; Hari, P ; Kulmala, M.'],
        'description': "atmospheric, flux, soil, tree physiological and water quality measurements at SMEAR Hyytiälä research station of the University of Helsinki."
                        "http://www.atm.helsinki.fi/SMEAR/"

    },
    {
        'title': "EnvThes; 1",
        'creator': ['EnvEurope, ExpeER, ILTER ; Peterseil, Kertesz, Frenzel, Schentz, Grandin, Bertrand, Blankman'],
        'description': "EnvThes with species of the Catalogue of Life"
    },
    {
        'title': "MORIS_CORE",
        'creator': ['Integrated Monitoring Group Austria'],
        'description': "Ontology of the Monitoring Research Information System."
                        "BASIS for all integrated Monitoring Ontologies"
    }
]

