# -*- coding: utf-8 -*-
# B2SHARE2

from __future__ import absolute_import


mock_records = [
    {
        'id': 1,
        'community_id': 1,
        'record_status': 'draft',
        'metadata': {
            # metadata schema id -> metadata object
            "0": {
                'title': "Jumping frogs in programming environments",
                'description': "A study on the distribution of frogs in IDEs; the implications.",
                'creator': 'John Smith',
                'open_access': True,
            },
        },
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
        ]
    }
]

