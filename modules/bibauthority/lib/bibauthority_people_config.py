# This file is part of Invenio.
# Copyright (C) 2015 CERN.
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

"""BibAuthority CERN People collection configuration file."""

from os.path import join

from invenio.config import(
    CFG_CACHEDIR,
    CFG_TMPSHAREDDIR
)

CFG_BIBAUTHORITY_LDAP_SEARCHFILTER = \
    r"(&(objectClass=*)(employeeType=Primary))"
CFG_BIBAUTHORITY_LDAP_ATTRLIST = [
    "employeeID",
    "givenName",
    "sn",
    "displayName",
    "facsimileTelephoneNumber",
    "telephoneNumber",
    "mobile",
    "mail",
    "department",
    "cernGroup",
    "description",
    "division",
    "extensionAttribute12",
    "cernInstituteName",
    "extensionAttribute11"
]  # Attributes used by Mapper.mapper_dict
CFG_BIBAUTHORITY_RECORDS_JSON_FILE = join(
    CFG_CACHEDIR,
    "records.json"
)
CFG_BIBAUTHORITY_RECORDS_UPDATES_FILE = join(
    CFG_TMPSHAREDDIR,
    "records_updates.xml"
)
CFG_BIBAUTHORITY_AUTHOR_CDS = "AUTHOR|(CDS)"
CFG_BIBAUTHORITY_AUTHOR_CERN = "AUTHOR|(SzGeCERN)"
CFG_BIBAUTHORITY_AUTHOR_INSPIRE = "AUTHOR|(INSPIRE)"
