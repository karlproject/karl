# Copyright (C) 2008-2009 Open Society Institute
#               Thomas Moroz: tmoroz@sorosny.org
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License Version 2 as published
# by the Free Software Foundation.  You may not use, modify or distribute
# this program under any other version of the GNU General Public License.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
"""Reconfigure the people directory based on an XML file.

Reindex if necessary.
"""

from ConfigParser import ConfigParser
from karl.models.interfaces import IProfile
from karl.models.peopledirectory import PeopleCategory
from karl.models.peopledirectory import PeopleDirectory
from karl.models.peopledirectory import PeopleReport
from karl.models.peopledirectory import PeopleReportGroup
from karl.models.peopledirectory import PeopleSection
from karl.models.peopledirectory import PeopleSectionColumn
from karl.scripting import get_default_config
from karl.scripting import open_root
from karl.security.policy import NO_INHERIT
from karl.utils import find_profiles
from karl.views.peopledirectory import COLUMNS
from lxml import etree
from repoze.bfg.security import Allow
from repoze.bfg.security import Deny
from repoze.bfg.traversal import model_path
import optparse
import os
import transaction

class ParseError(Exception):
    def __init__(self, msg, elem):
        self.msg = msg
        self.sourceline = elem.sourceline
        docinfo = getattr(elem.getroottree(), 'docinfo', None)
        if docinfo is not None:
            self.url = docinfo.URL
        else:
            self.url = None

    def __str__(self):
        res = "%s on line %d" % (self.msg, self.sourceline)
        if self.url:
            res += ' of %s' % self.url
        return res

def id_and_title(elem):
    id = elem.get('id')
    if not id:
        raise ParseError("Missing id attribute", elem)
    title = elem.get('title', id)
    return id, title

def set_acl(obj, obj_elem):
    acl_elem = obj_elem.find('acl')
    if acl_elem is None:
        return
    acl = []
    for e in acl_elem:
        if e.tag in ('allow', 'deny'):
            principal = e.get('principal')
            if not principal:
                raise ParseError("Missing principal attribute", e)
            permission = e.get('permission')
            if not permission:
                raise ParseError("Missing permission attribute", e)
            if e.tag == 'allow':
                ace = (Allow, principal, permission)
            else:
                ace = (Deny, principal, permission)
        elif e.tag == 'no-inherit':
            ace = NO_INHERIT
        else:
            raise ParseError("Unrecognized element", e)
        acl.append(ace)
    obj.__acl__ = acl

def parse_report(people, elem):
    reportid, title = id_and_title(elem)
    link_title = elem.get('link-title', title)
    css_class = elem.get('class', 'general')
    obj = PeopleReport(title, link_title, css_class)
    for e in elem.findall('filter'):
        catid = e.get('category')
        values = e.get('values', '').split()
        pc = people.categories.get(catid)
        if pc is None:
            raise ParseError("No such category defined", e)
        if not values:
            raise ParseError("No category values given", e)
        for v in values:
            if v not in pc:
                raise ParseError("No such category value: %s" % v, e)
        obj.set_filter(catid, values)
    columns = None
    e = elem.find('columns')
    if e is not None:
        columns = e.get('ids', '').split()
    if not columns:
        raise ParseError("No columns given", elem)
    for colid in columns:
        if not colid in COLUMNS:
            raise ParseError("No such column defined: %s" % colid, e)
    obj.set_columns(columns)
    return reportid, obj

def parse_reports(people, parent_elem, reportmap):
    contents = []
    for e in parent_elem:
        if e.tag == 'report-group':
            obj = PeopleReportGroup(e.get('title'))
            obj.set_reports(parse_reports(people, e, reportmap))
            contents.append(obj)
        elif e.tag == 'report':
            reportid, obj = parse_report(people, e)
            if reportid in reportmap:
                raise ParseError("Non-unique report ID", e)
            reportmap[reportid] = obj
            contents.append(obj)
        else:
            raise ParseError('Unrecognized element', e)
    return contents

def parse_section(people, section_elem):
    columns = []
    reportmap = {}
    single = False
    for e in section_elem:
        if e.tag == 'report':
            if columns:
                raise ParseError(
                    'Section has both columns and a single report', e)
            if reportmap:
                raise ParseError(
                    'Multiple reports provided for a single report section', e)
            single = True
            reportid, obj = parse_report(people, e)
            reportmap[reportid] = obj
        elif e.tag == 'column':
            if single:
                raise ParseError(
                    'Section has both columns and a single report', e)
            obj = PeopleSectionColumn()
            obj.set_reports(parse_reports(people, e, reportmap))
            columns.append(obj)
        elif e.tag == 'acl':
            pass
        else:
            raise ParseError('Unrecognized element', e)
    return columns, reportmap

def peopleconf(peopledir, tree):
    peopledir.categories.clear()
    for cat_elem in tree.findall('categories/category'):
        catid, title = id_and_title(cat_elem)
        pc = PeopleCategory(title)
        peopledir.categories[catid] = pc
        for value_elem in cat_elem.findall('value'):
            valueid, title = id_and_title(value_elem)
            pc[valueid] = title

    for secid in list(peopledir.keys()):
        del peopledir[secid]

    section_order = []
    for section_elem in tree.findall('sections/section'):
        secid, title = id_and_title(section_elem)
        section_order.append(secid)
        tab_title = section_elem.get('tab-title', title)
        section = PeopleSection(title, tab_title)
        peopledir[secid] = section
        set_acl(section, section_elem)

        columns, reportmap = parse_section(peopledir, section_elem)
        section.set_columns(columns)
        for k, v in reportmap.items():
            section[k] = v

    peopledir.set_order(section_order)

    need_reindex = peopledir.update_indexes()
    if need_reindex:
        reindex(peopledir)

def reindex(peopledir):
    catalog = peopledir.catalog
    document_map = catalog.document_map
    profiles = find_profiles(peopledir)
    for obj in profiles.values():
        if IProfile.providedBy(obj):
            path = model_path(obj)
            docid = document_map.docid_for_address(path)
            if not docid:
                docid = document_map.add(path)
                catalog.index_doc(docid, obj)
            else:
                catalog.reindex_doc(docid, obj)

def main():
    parser = optparse.OptionParser(description=__doc__)
    parser.add_option('-C', '--config', dest='config',
        help='Path to configuration file (defaults to etc/karl.ini)',
        metavar='FILE')
    parser.add_option('--dry-run', dest='dryrun',
        action='store_true', default=False,
        help="Don't actually commit the transaction")
    options, args = parser.parse_args()
    if args:
        parser.error("Too many parameters: %s" % repr(args))

    config = options.config
    if config is None:
        config = get_default_config()
    root, closer = open_root(config)

    cp = ConfigParser()
    cp.read(config)
    fn = os.path.join(os.path.dirname(config), cp.get('peopleconf', 'file'))
    tree = etree.parse(fn)

    try:
        if not isinstance(root.get('people'), PeopleDirectory):
            # remove the old people directory
            del root['people']
        if 'people' not in root:
            root['people'] = PeopleDirectory()
        peopleconf(root['people'], tree)
    except:
        transaction.abort()
        raise
    else:
        if options.dryrun:
            transaction.abort()
        else:
            transaction.commit()

if __name__ == '__main__':
    main()
