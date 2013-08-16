## This file is part of Invenio.
## Copyright (C) 2006, 2007, 2008, 2009, 2010, 2011 CERN.
##
## Invenio is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## Invenio is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Invenio; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
"""BibFormat element - Prints server info
"""
__revision__ = "$Id$"


def format_element(bfo):

    ret = '<div class="metadata_table"><table class="table table-striped'\
          ' table-condensed">'

    # Might be more than one of these - need for each
    pid = bfo.field("0247_")
    if pid['2'] == 'PID':
        ret += '<tr><th>PID:</th><td>{}</td></tr>'.format(pid['a'])

    ver = bfo.field("250__a")
    if ver:
        ret += '<tr><th>Version:</th><td>{}</td></tr>'.format(ver)

    # argh - used SimpleStore here. Fix :(
    pub = bfo.field("264__b")
    if pub:
        ret += '<tr><th>Publication:</th><td>{}</td></tr>'.format(pub)

    pub_date = bfo.field("264__c")
    if pub_date:
        ret += '<tr><th>Publication Date:</th><td>{}</td></tr>'.format(pub_date)

    licence = bfo.field("540__a")
    if licence:
        ret += '<tr><th>Licence:</th><td>{}</td></tr>'.format(licence)

    uploader = bfo.field("8560_f")
    if uploader:
        ret += '<tr><th>Uploaded by:</th><td>{}</td></tr>'.format(uploader)

    ret += '</table></div>'
    # ret += 'Uploaded by <a href="' + url_for('yourmessages.write', sent_to_user_nicks=bfo.field('8560_y')) + '">' + bfo.field('8560_y').decode('utf8') + '</a>'
    return  ret


def escape_values(bfo):
    return 0
