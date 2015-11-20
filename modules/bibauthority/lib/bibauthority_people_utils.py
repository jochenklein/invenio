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

from json import dump, load
from invenio.bibtask import task_low_level_submission
from invenio.websubmit_author_sources.atlas_glance import (
    _query_atlas_glance_authors)
from os import makedirs
from os.path import dirname, exists, isfile


class UtilsError(Exception):
    """Base class for exceptions in this module."""
    pass


def bibupload(file, cmd_options, name, priority="-1"):
    """Upload file to CDS using invenio.bibtask.task_low_level_submission.

    :param filepath file: XML file (MARC 21 XML Schema) containing records
    :param string cmd_options: see task_low_level_submission command options
    :param string name: task specific name
    :param string priority: task priority (0=default, 1=higher, etc)
    :return: task id, None if file not found
    """
    task_id = None
    if isfile(file):
        task_id = task_low_level_submission(
            "bibupload",  # Name
            "bibauthority-people",  # User
            cmd_options, file,
            "-P", priority,
            "-N", name)
    return task_id


def get_inspire_id_from_atlas_glance(employee_id):
    """Get the Inspire-ID, given the CERN-ID (employeeID).

    :param string employee_id: CERN-ID (employeeID)
    :result: Inspire-ID or None
    """
    inspire_id = None
    results, error = _query_atlas_glance_authors(cernccid_equals=employee_id)

    if not error:
        if results and len(results) == 1:
            result = results[0]
            inspire_id = result.get("inspireid", "").strip() or None

    return inspire_id


def get_inspire_id_from_atlas_glance_local(employee_id, mapping):
    """Get the Inspire-ID, given the CERN-ID (employeeID) and mapping
    (employeeID: Inspire-ID).

    :param string employee_id: CERN-ID (employeeID)
    :return: Inspire-ID or None
    """
    return mapping.get(str(employee_id))


def json_to_list(file):
    """Transform JSON file to python list.

    :param filepath file: path to JSON file containing records
    :return: list of records or empty list
    """
    records = []
    try:
        with open(file) as f:
            try:
                records = load(f)
            except ValueError as e:
                raise UtilsError(
                    "Error: failed loading records from file. ({0})".format(e))
    except EnvironmentError as e:
        raise UtilsError(
            "Error: failed opening file '{0}'. ({1})".format(file, e))
    return records


def diff_records(records_ldap, records_local):
    """Compare records with same employeeID and classify between
    changed ('change'), new ('add'), and removed ('remove') records.

    :param list records_ldap: fetched CERN LDAP records
    :param list records_local: previous fetched CERN LDAP records, saved as a
        JSON file
    :return: list of updated records (tuple: (status, record)), where
        status = 'change', 'add', or 'remove', or empty list
    """
    # Transform list of records to dictionary:
    # [{record}, ...] -> {'employeeID': {record}, ...}
    results = []
    try:
        dict_ldap = dict((x.get('employeeID')[0], x) for x in records_ldap)
        dict_local = dict((x.get('employeeID')[0], x) for x in records_local)

        for record in records_ldap:
            employee_id = record.get('employeeID')[0]
            # Changed record
            if employee_id in dict_local.keys():
                # Compare each (key, value) of two records
                for attr in record:
                    if not record.get(attr) == dict_local.get(
                      employee_id).get(attr):
                        results.append(('change', record))
                        break
            # New record
            else:
                results.append(('add', record))

        for record in records_local:
            # Removed record
            if not record.get('employeeID')[0] in dict_ldap:
                results.append(('remove', record))
    except (TypeError, IndexError) as e:
        raise UtilsError("No attribute 'employeeID' found. {0}".format(e))

    return results


def export_json(records, file):
    """Export records to file using json.dump.

    :param list records: list of records
    :param filepath file: path to JSON file containing records
    """
    directory = dirname(file)
    if directory is not "" and not exists(directory):
        makedirs(directory)

    try:
        with open(file, "w") as f:
            try:
                dump(records, f)
            except ValueError as e:
                raise UtilsError(
                    "Error: failed dumping records to JSON. ({0})"
                    .format(e))
    except EnvironmentError as e:
        raise UtilsError(
            "Error: failed opening file. ({0})".format(e))
