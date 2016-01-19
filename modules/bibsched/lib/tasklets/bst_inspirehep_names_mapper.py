# This file is part of Invenio.
# Copyright (C) 2016 CERN.
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

"""INSPIRE-HEP IDs to names mapping (Invenio Bibliographic Tasklet).

Harvest records on INSPIRE-HEP including MARC fields 035__9 and 035__a. Map
INSPIRE-IDs to INSPIRE-HEP-names, and write the dictionary to a JSON file.

Output example: {"INSPIRE-12345": "john.1", ...}

Usage:
$bibtasklet -N inspirehep-names-mapper
    -T bst_inspirehep_names_mapper [-a json_file
        [default: invenio.config.CFG_CACHEDIR/inspirehep-names-mapping.json]]
"""

import time
import urllib2
import xml.etree.ElementTree as ET
from os.path import join
from sys import stderr

from invenio.bibauthority_people_utils import (
    export_json, UtilsError, version_file)
from invenio.bibtask import write_message
from invenio.config import CFG_CACHEDIR

INSPIREHEP_NAMES_MAPPING_FILE = join(
    CFG_CACHEDIR, "inspirehep-names-mapping.json")
ns = {"x": "http://www.loc.gov/MARC21/slim"}  # XML namespaces


def get_records(record_limit=250):
    """Get MARCXML record elements.

    :param int record_limit: records limit each request. Maximum 251,
        except if you are a superadmin
    :return: list of MARCXML record elements or empty list
    """
    counter = 1
    records_all = []

    url = (
        "https://inspirehep.net/search?cc=HepNames"
        "&p=035__9%3ABAI+035__%3AINSPIRE&of=xm&ot=035&rg={0}&jrec={1}")

    while 1:
        req = urllib2.Request(url.format(record_limit, counter))
        try:
            response = urllib2.urlopen(req)
        except urllib2.URLError as e:
            raise e
        page_result = response.read()
        root = ET.fromstring(page_result)
        records = root.findall(".//x:record", namespaces=ns) or []

        if not records:
            break

        records_all = records_all + records
        counter += record_limit

        # Sleep some seconds between every request not to be banned
        time.sleep(3)

    return records_all


def get_mapping(inspire_records):
    """Get mapping INSPIRE-ID to INSPIRE-HEP-name.

    :param list inspire_records: list of MARCXML record elements
    :return: dictionary containing the mapping
    """
    inspire_mapping = {}

    for record in inspire_records:
        inspire_id = inspire_name = None

        datafields = record.findall("x:datafield[@tag='035']", namespaces=ns)
        for datafield in datafields:
            subfield = datafield.find("x:subfield[@code='9']", namespaces=ns)
            if subfield is not None:
                subfield_a = datafield.find(
                    "x:subfield[@code='a']", namespaces=ns)
                if subfield_a is not None:
                    if (subfield.text == "INSPIRE"):
                        inspire_id = subfield_a.text
                    elif (subfield.text == "BAI"):
                        inspire_name = subfield_a.text

        inspire_mapping[inspire_id] = inspire_name

    return inspire_mapping


def bst_inspirehep_names_mapper(json_file=INSPIREHEP_NAMES_MAPPING_FILE):
    """Map INSPIRE-IDs to INSPIRE-HEP-names and write to JSON.

    :param filepath json_file: path to JSON file containing the INSPIRE mapping
    """
    try:
        records = get_records()
        write_message("{0} records (HepNames) fetched.".format(len(records)))
        mapping = get_mapping(records)
        if mapping:
            version_file(json_file, 1)
            try:
                export_json(mapping, json_file)
                write_message(
                    "Mapping for INSPIRE-HEP-ids and -names exported to JSON. "
                    "See '{0}'.".format(json_file))
            except UtilsError as e:
                write_message(e.reason, stderr)
    except urllib2.URLError as e:
        write_message(e.reason, stderr)
