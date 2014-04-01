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

"""BibFormat element - Prints server info
"""
__revision__ = "$Id$"

from invenio.simplestore_model import metadata_classes


def format_element(bfo):

    ret = '<div><table class="metadata_table table table-striped'\
          ' table-condensed">'

    ver = bfo.field("250__a")
    if ver:
        ret += '<tr><th>Version:</th><td>{0}</td></tr>'.format(ver)

    pub = bfo.field("260__")
    if pub:
        ret += '<tr><th>Publication:</th><td>{0}</td></tr>'.format(pub.get('b'))
        if 'c' in pub:
            ret += '<tr><th>Publication Date:</th><td>{0}</td></tr>'.format(
                   pub['c'])

    licence = bfo.field("540__a")
    if licence:
        ret += '<tr><th>Licence:</th><td>{0}</td></tr>'.format(licence)

    uploader = bfo.field("8560_f")
    if uploader:
        ret += '<tr><th>Uploaded by:</th><td>{0}</td></tr>'.format(uploader)

    domain = bfo.field("980__a")
    if domain:
        ret += '<tr><th>Domain:</th><td>{0}</td></tr>'.format(domain)

    md_class = None
    if domain.lower() in metadata_classes:
        md_class = metadata_classes[domain.lower()]()

    domain_data = bfo.fields("690__")
    for md in domain_data:
        if md_class:
            field = md_class.field_args.get(md['a'], {'label': md['a']})
        else:
            field = {'label': md['a']}
        ret += '<tr><th>{0}:</th><td>{1}</td></tr>'.format(
            field['label'], md['b'])

    ids = bfo.fields("0247_")
    for i in ids:
        val = i['a']
        if i['2'] == "PID":
            try:
                val = '<a href="{0}">{0}</a>'.format(i['a'])
            except ImportError:
                None

        ret += '<tr><th width="40%">{0}:</th><td width="60%">{1}</td></tr>'.format(
            i['2'][0].upper() + i['2'][1:], val)

    ret += '</table></div>'

    return  ret


def escape_values(bfo):
    return 0
