# -*- coding: utf-8 -*-
#
# This file is part of EUDAT B2Share.
# Copyright (C) 2016 University of Tuebingen, CERN.
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
from b2share.modules.records.providers import RecordUUIDProvider
from flask import Blueprint, abort, current_app, jsonify, request
from invenio_files_rest import models as fm
from invenio_records.api import Record
from invenio_rest import ContentNegotiatedMethodView

blueprint = Blueprint('b2share_apilinkset', __name__, url_prefix='/linkset/<path:record_id>/json')

@blueprint.url_value_preprocessor
def get_record_value(endpoint, values):
    print(values)
    rec = values['record_id']
    print(rec)


class ApiLinkset(ContentNegotiatedMethodView):
    def __init__(self, **kwargs):
        """Constructor.
        :param resolver: Persistent identifier resolver instance.
        """
        default_media_type = 'application/json'
        super(ApiLinkset, self).__init__(
            serializers={
                'application/json': lambda response: jsonify(response)
            },
            default_method_media_type={
                'GET': default_media_type,
            },
            default_media_type=default_media_type,
            **kwargs)

    def get(self, **kwargs):
        input_record = request.view_args['record_id']
        if input_record is None:
            return abort(400)

        linkset = []
        try:
            rec_pid = RecordUUIDProvider.get(input_record).pid
            record = Record.get_record(rec_pid.object_uuid)
            landingpage = current_app.config.get(
                'PREFERRED_URL_SCHEME',
                '') + '://' + current_app.config.get(
                'JSONSCHEMAS_HOST', '') + '/records/' + input_record

            citations = []
            doi_identifier = None
            for p in record.get('_pid'):
                if p.get('type') == 'DOI':
                    doi_identifier = p.get('value')
                    cite = {'href' : 'https://doi.org/' + doi_identifier}
                    citations.append(cite)

            if doi_identifier is None and record.get('alternate_identifiers') is not None:
                for ai in record.get('alternate_identifiers'):
                    if ai.get('alternate_identifier_type') == 'DOI':
                        doi_identifier = ai.get('alternate_identifier')
                        cite = {'href' : 'https://doi.org/' + doi_identifier}
                        citations.append(cite)
            hdl_identifer = None
            if doi_identifier is None:
                #Identifier is required
                current_app.logger.error('No alternate_identifiers')

            rec_license = record.get('license')
            license = {}
            if rec_license is not None:
                license = { 'href': rec_license.get('license_uri')}
            else:
                print('No license')

            describedbys = []
            if doi_identifier is not None:
                describedby = {'href':'https://citation.crosscite.org/format?style=bibtex&doi=' + doi_identifier,
                               'type':'application/x-bibtex'}
                describedbys.append(describedby)
            items = []
            # item_landingpage = {'href': landingpage, 'type':'text/html'}
            # items.append(item_landingpage)
            fs = []
            # print(record)
            for file in record.get('_files', []):
                print(file)
                fmimetype = fm.ObjectVersion.get(
                    file.get('bucket'), file.get('key'),
                    file.get('version_id')).mimetype
                file_location = current_app.config.get(
                    'PREFERRED_URL_SCHEME',
                    '') + '://' + current_app.config.get(
                    'JSONSCHEMAS_HOST', '') + '/api/files/' + file.get(
                    'bucket') + '/' + file.get('key')
                file.update({'file-location': file_location})
                print(file_location)
                print(fmimetype)
                item_file = {'href': file_location, 'type':fmimetype}
                items.append(item_file)
                item_anchor = {'anchor':file_location, 'collection':[{'href':landingpage, 'type':'text/html'}]}
                fs.append(item_anchor)

            types = []
            type_about_page = {'href':'https://schema.org/AboutPage'}
            types.append(type_about_page)
            element = {'anchor': landingpage, 'type':types, 'cite-as': citations, 'item':items, 'describedby':describedbys, 'license':license}
            linkset.append(element)
            for a in fs:
                linkset.append(a)
            return {'linkset': linkset}
        except:
            return abort(404)

blueprint.add_url_rule('', view_func=ApiLinkset.as_view('linkset'))
