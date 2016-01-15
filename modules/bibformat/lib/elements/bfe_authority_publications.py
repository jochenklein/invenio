# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2006, 2007, 2008, 2009, 2010, 2011, 2015, 2016 CERN.
#
# Invenio is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
"""BibFormat element - Prints the control number of an Authority Record.
"""

from invenio.bibauthority_config import (
    CFG_BIBAUTHORITY_AUTHORITY_COLLECTION_NAME,
    CFG_BIBAUTHORITY_RECORD_CONTROL_NUMBER_FIELD,
    CFG_BIBAUTHORITY_RECORD_AUTHOR_CONTROL_NUMBER_FIELDS as control_number_fields)
from invenio.bibauthority_engine import ( 
    get_low_level_recIDs_from_control_no,
    get_dependent_records_for_control_no)
from invenio.config import CFG_SITE_URL, CFG_SITE_NAME
from invenio.search_engine import get_fieldvalues, perform_request_search


CFG_BIBAUTHORITY_PUBLICATION_VIEW_LIMIT = 10
__revision__ = "$Id$"


def get_record_ids_for_authority_ids(authority_ids, author_full_name):
    """Return list of record ids for a given authority ids (control numbers).

    If no record ids have been found for the given ids, do a search based
    on the author's full name, stored in the field `100__a`.

    :param list authority_id: authority ids (also known as control numbers)
    :param str author_full_name: if no record ids have been found for the given
        authority_id, search by author_full_name

    :return: list of record ids, or empty list, if no record ids have been found
    """
    record_ids = []
    for authority_id in authority_ids:
        record_ids.extend(get_dependent_records_for_control_no(authority_id))
        record_ids.extend(get_dependent_records_for_control_no(
            authority_id.replace("AUTHOR|(SzGeCERN)", "CERN-")))
        record_ids.extend(get_dependent_records_for_control_no(
            authority_id.replace("AUTHOR|(SzGeCERN)", "CCID-")))
        if not record_ids:
            record_ids.extend(get_dependent_records_for_control_no(
                authority_id.replace("AUTHOR|(INSPIRE)", "")))

    if not record_ids:
        # No record ids for the given authority ids have been found
        # Search for record ids using the author's full name
        record_ids.extend(perform_request_search(
            p="author:\"{0}\"".format(author_full_name)))

    # Remove possible duplicates
    return list(set(record_ids))


def format_element(bfo, print_title="yes"):
    """ Prints the control number of an author authority record in HTML.
    By default prints brief version.
    @param brief: whether the 'brief' rather than the 'detailed' format
    @type brief: 'yes' or 'no'
    """
    from invenio.messages import gettext_set_language
    _ = gettext_set_language(bfo.lang)    # load the right message language

    control_nos = [d['a'] for d in bfo.fields('035__') if d.get('a')]
    control_nos.append("AUTHOR|(CDS){0}".format(bfo.control_field("001")))

    publications_formatted = []
    record_ids = get_record_ids_for_authority_ids(control_nos,
                                                  bfo.field("100__a"))
    # if we have dependent records, provide a link to them
    if record_ids:
        prefix_pattern = "<a href='" + CFG_SITE_URL + "%s" + "'>"
        postfix = "</a>"
        url_str = ''
        # Print as many of the author's publications as the
        # CFG_BIBAUTHORITY_PUBLICATION_VIEW_LIMIT allows
        for i in range(
                len(record_ids) if
                len(record_ids) < CFG_BIBAUTHORITY_PUBLICATION_VIEW_LIMIT else
                CFG_BIBAUTHORITY_PUBLICATION_VIEW_LIMIT):
            title = get_fieldvalues(record_ids[i], "245__a")
            if not title:
                break
            url_str = "/record/"+ str(record_ids[i])
            prefix = prefix_pattern % url_str
            publications_formatted.append(prefix + title[0] + postfix)

    result = ""
    if publications_formatted:
        result = ("<ol><li>" +
                  "</li><li> ".join(publications_formatted) +
                  "</li></ol>")
    url_str = (
        "/search" +
        "?p=" + "author:\"{0}\"".format(bfo.field("100__a")) +
        "&ln=" + bfo.lang)
    if result:
        prefix = prefix_pattern % url_str
        result += prefix + "See more publications" + postfix
        if print_title.lower() == "yes":
            title = "<strong>" + _("Publication(s)") + "</strong>"
            result = title + ": " + result

    return result


def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
