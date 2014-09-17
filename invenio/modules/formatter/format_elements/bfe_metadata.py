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

from invenio.b2share.modules.b2deposit.b2share_model import metadata_classes

def format_element(bfo):

    ret = '<div><table class="metadata_table table table-striped'\
          ' table-condensed">'

    html = '<tr><th><div style="white-space:nowrap">{0}:</div></th><td><div style="word-break:break-all">{1}</div></td></tr>'

    ids = bfo.fields("0247_")
    for i in ids:
        val = i['a']
        if i['2'] == "PID":
            try:
                val = '<a href="{0}">{0}</a>'.format(i['a'])
            except ImportError:
                None
            ret += html.format(i['2'][0].upper() + i['2'][1:], val)

    ver = bfo.field("250__a")
    if ver:
        ret += html.format('Version', ver)

    pub = bfo.field("260__")
    if pub:
        ret += html.format('Publication', pub.get('b'))
        if 'c' in pub:
            ret += html.format('Publication Date', pub['c'])

    licence = bfo.field("540__a")
    if licence:
        ret += html.format('Licence', licence)

    uploader = bfo.field("8560_f")
    if uploader:
        ret += html.format('Uploaded by', uploader)

    contact_email = bfo.field("270__m")
    if contact_email:
        ret += html.format('Contact email', contact_email)

    domain = bfo.field("980__a")
    if domain:
        ret += html.format('Domain', domain)

    md_class = None
    if domain.lower() in metadata_classes():
        md_class = metadata_classes()[domain.lower()]()

    domain_data = bfo.fields("690__")
    for md in domain_data:
        if md_class:
            field = md_class.field_args.get(md['a'], {'label': md['a']})
        else:
            field = {'label': md['a']}
        ret += html.format(field['label'], md['b'])

    ids = bfo.fields("0247_")
    for i in ids:
        val = i['a']
        if i['2'] != "PID":
            ret += html.format(i['2'][0].upper() + i['2'][1:], val)

    ret += '</table></div>'

    return  ret


def escape_values(bfo):
    return 0
