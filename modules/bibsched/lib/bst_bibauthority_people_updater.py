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

"""Invenio Bibliographic Tasklet for updating CERN People Collection on the
CERN Document Server. The collection is based on data fetched from CERN LDAP,
including the Inspire-ID from ATLAS GLANCE.

Usage:
$bibtasklet -N bibauthority-people -T bst_bibauthority_people_updater [-a file
    [default: invenio.bibauthority_people_config.CFG_RECORDS_JSON_FILE]]
"""

from sys import stderr
from invenio.bibauthority_people_config import (
    CFG_BIBAUTHORITY_LDAP_ATTRLIST, CFG_BIBAUTHORITY_LDAP_SEARCHFILTER,
    CFG_BIBAUTHORITY_RECORDS_JSON_FILE, CFG_BIBAUTHORITY_RECORDS_UPDATES_FILE)
from invenio.bibauthority_people_mapper import Mapper, MapperError
from invenio.bibauthority_people_utils import (
    bibupload, diff_records, export_json, json_to_list, UtilsError)
from invenio.bibtask import write_message
from invenio.ldap_cern import get_users_records_data, LDAPError


def update(records_updates):
    """Map updated records in record_diff and upload to CDS.

    :param list records_updates: list of tuples (status, record), where status
        is 'add', 'remove', or 'change'
    """
    write_message("{0} updated record(s) detected".format(
        len(records_updates)))
    if len(records_updates):
        try:
            # Map updated records
            mapper = Mapper()
            mapper.update_ldap_records(records_updates)

            # Write updates to XML
            mapper.write_marcxml(CFG_BIBAUTHORITY_RECORDS_UPDATES_FILE, 0)

            # Upload updates to CDS using --replace and --insert
            task_id = bibupload(CFG_BIBAUTHORITY_RECORDS_UPDATES_FILE, "-ri",
                                "bibauthority-people-update")
            if task_id:
                write_message(
                    "Task (identifier: {0}) is correctly enqueued"
                    .format(task_id))
            else:
                write_message("Error: failed to enqueue task",
                              stderr)
        except MapperError as e:
            write_message(e, stderr)


def bst_bibauthority_people_updater(file=CFG_BIBAUTHORITY_RECORDS_JSON_FILE):
    """Update CDS records with current CERN LDAP records.

    :param filepath file: path to JSON file containing records
    """
    try:
        # Fetch CERN LDAP records
        records_ldap = get_users_records_data(
            CFG_BIBAUTHORITY_LDAP_SEARCHFILTER, CFG_BIBAUTHORITY_LDAP_ATTRLIST)
        write_message("{0} records fetched from CERN LDAP"
                      .format(len(records_ldap)))
        try:
            records_local = json_to_list(file)

            # records_diff contains updated records (changed, added, or
            # removed on LDAP)
            records_diff = diff_records(records_ldap, records_local)

            try:
                update(records_diff)
                # Update local file with current LDAP records
                export_json(records_ldap, file)
            except UtilsError as e:
                write_message(e, stderr)
        except UtilsError as e:
            write_message(e, stderr)
    except LDAPError as e:
        write_message(e, stderr)
