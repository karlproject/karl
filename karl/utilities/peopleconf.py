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
from lxml import etree
from pyramid.security import Allow
from pyramid.security import Deny
from pyramid.security import DENY_ALL
from pyramid.traversal import resource_path
from pyramid.url import resource_url
from chameleon.zpt.template import PageTemplate

from karl.models.interfaces import IPeopleRedirector
from karl.models.interfaces import IPeopleReport
from karl.models.interfaces import IPeopleReportCategoryFilter
from karl.models.interfaces import IPeopleReportGroup
from karl.models.interfaces import IPeopleReportGroupFilter
from karl.models.interfaces import IPeopleReportIsStaffFilter
from karl.models.interfaces import IPeopleReportMailingList
from karl.models.interfaces import IPeopleSection
from karl.models.interfaces import IPeopleSectionColumn
from karl.models.peopledirectory import PeopleCategories
from karl.models.peopledirectory import PeopleCategory
from karl.models.peopledirectory import PeopleCategoryItem
from karl.models.peopledirectory import PeopleRedirector
from karl.models.peopledirectory import PeopleReport
from karl.models.peopledirectory import PeopleReportCategoryFilter
from karl.models.peopledirectory import PeopleReportGroup
from karl.models.peopledirectory import PeopleReportGroupFilter
from karl.models.peopledirectory import PeopleReportIsStaffFilter
from karl.models.peopledirectory import PeopleReportMailingList
from karl.models.peopledirectory import PeopleSection
from karl.models.peopledirectory import PeopleSectionColumn
from karl.models.peopledirectory import reindex_peopledirectory
from karl.security.policy import NO_INHERIT
from karl.utils import find_site

def _acl_info(section):
    result = {'inherit': True}
    aces = result['aces'] = []
    for ace in getattr(section, '__acl__', ()):
        if ace == DENY_ALL:
            result['inherit'] = False
            break
        verb, principal, permission = ace
        aces.append((verb.lower(), principal, permission))
    return result


def _section_info(item, reqport):
    return {'type': 'section',
            'title': item.title,
            'tab_title': item.tab_title,
            'acl': _acl_info(item),
           }


def _column_info(item, reqport):
    return {'type': 'column',
           }


def _group_info(item, reqport):
    return {'type': 'report-group',
            'title': item.title,
           }


def _report_info(item, reqport):
    info = {'type': 'report',
            'title': item.title,
            'link_title': item.link_title,
            'css_class': item.css_class,
            'columns': list(item.columns),
           }
    return info


def _category_filter_info(item, request):
    return {'type': 'filter-category',
            'values': list(item.values),
           }


def _group_filter_info(item, request):
    return {'type': 'filter-group',
            'values': list(item.values),
           }


def _is_staff_filter_info(item, request):
    return {'type': 'filter-isstaff',
            'values': [str(item.include_staff)],
           }


def _mailinglist_info(item, reqport):
    return {'type': 'mailinglist',
            'short_address': item.short_address,
           }


def _redirector_info(item, reqport):
    return {'type': 'redirector',
            'target_url': item.target_url,
           }


_DISPATCH = [
    (IPeopleSection, _section_info, False),
    (IPeopleSectionColumn, _column_info, False),
    (IPeopleReportGroup, _group_info, False),
    (IPeopleReport, _report_info, False),
    (IPeopleReportCategoryFilter, _category_filter_info, True),
    (IPeopleReportGroupFilter, _group_filter_info, True),
    (IPeopleReportIsStaffFilter, _is_staff_filter_info, True),
    (IPeopleReportMailingList, _mailinglist_info, True),
    (IPeopleRedirector, _redirector_info, True),
]

def _subitem_info(item, request):
    infos = []
    order = getattr(item, 'order', item.keys())
    for name in order:
        sub = item[name]
        infos.append(peopledir_item_model(sub, request))
    return infos


def peopledir_item_model(context, request):
    info = {'name': context.__name__,
            'url': resource_url(context, request),
           }
    for iface, info_maker, leaf in _DISPATCH:
        if iface.providedBy(context):
            info.update(info_maker(context, request))
            break
    if not leaf:
        info['items'] = _subitem_info(context, request)
    return info


def peopledir_model(context, request):
    categories = []
    for category_id, category in sorted(context['categories'].items()):
        c_info = {'name': category_id,
                  'url': resource_url(category, request),
                  'title': category.title,
                 }
        values = c_info['values'] =  []
        for value_id, value in sorted(category.items()):
            v_info = {'name': value_id,
                      'url': resource_url(value, request),
                      'title': value.title,
                      'description': value.description,
                     }
            values.append(v_info)
        categories.append(c_info)
    sections = _subitem_info(context, request)
    return {'categories': categories, 'sections': sections}

# XXX Let these die just as soon as we haee the JSON working
_DUMP_XML =  """\
<?xml version="1.0" encoding="UTF-8"?>
<peopledirectory>
 <categories>
  <category tal:repeat="(c_id, category) sorted(categories.items())"
            name="${c_id}"
            title="${category.title}">
   <value tal:repeat="(v_id, value) sorted(category_items(category))"
            name="${v_id}"
            title="${value.title}"
            tal:content="structure value.description">DESCRIPTION</value>
  </category>
 </categories>
 <sections>
  <section tal:repeat="(s_id, section) sections"
           name="${s_id}"
           title="${section.title}"
           tab-title="${section.tab_title}">
   <acl tal:define="info acl_info(section)">
    <tal:loop tal:repeat="(verb, principal, permissions) info['aces']">
     <allow tal:condition="verb == 'allow'"
            principal="${principal}">
      <permission tal:repeat="permission permissions"
      >${permission}</permission>
     </allow>
     <deny tal:condition="verb == 'deny'"
           principal="${principal}">
      <permission tal:repeat="permission permissions"
      >${permission}</permission>
     </deny>
    </tal:loop>
    <no-inherit tal:condition="not info['inherit']"/>
   </acl>
   <column tal:repeat="(name, column) column_info(section)"
           tal:attributes="name name">
    <tal:defs tal:define="nested report_items(column)">
     <tal:loop tal:repeat="(r_id, item) nested">
      <metal:block tal:condition="is_group(item)"
                   metal:use-macro="macros['report_group']" />
      <metal:block tal:condition="not is_group(item)"
                   metal:use-macro="macros['report']" />
     </tal:loop>
    </tal:defs>
   </column>
   <tal:loop tal:repeat="(r_id, item) sorted(section.items())">
    <metal:chunk metal:define-macro="column">
     <column tal:condition="is_column(item)"
             name="${r_id}">
      <tal:defs tal:define="nested report_items(item)">
       <tal:loop tal:repeat="(r_id, item) nested">
        <metal:block metal:use-macro="macros['report_group']" />
        <metal:block metal:use-macro="macros['report']" />
       </tal:loop>
      </tal:defs>
     </column>
    </metal:chunk>
    <metal:chunk metal:define-macro="report_group">
     <report-group tal:condition="is_group(item)"
                   name="${r_id}"
                   title="${item.title}">
      <tal:defs tal:define="nested report_items(item)">
       <tal:loop tal:repeat="(r_id, item) nested">
        <metal:block metal:use-macro="macros['report']" />
       </tal:loop>
      </tal:defs>
     </report-group>
    </metal:chunk>
    <metal:chunk metal:define-macro="report">
     <report tal:condition="is_report(item)"
             name="${r_id}"
             title="${item.title}"
             link-title="${item.link_title}"
             class="${item.css_class}">
      <tal:loop tal:repeat="info report_filter_items(item)">
       <filter tal:condition="info['type'] == 'category'"
               name="${info['name']}"
               type="${info['type']}"
               category="${info['name']}"
               values="${info['values']}"/>
       <filter tal:condition="info['type'] == 'groups'"
               name="${info['name']}"
               type="${info['type']}"
               values="${info['values']}"/>
       <filter tal:condition="info['type'] == 'is_staff'"
               name="${info['name']}"
               type="${info['type']}"
               include_staff="${info['include_staff']}"/>
      </tal:loop>
      <mailinglist tal:condition="'mailinglist' in item"
                   tal:attributes="short_address
                                        item['mailinglist'].short_address"/>
      <columns names="${' '.join(item.columns)}"/>
     </report>
    </metal:chunk>
    <metal:chunk metal:define-macro="redirector">
     <redirector tal:condition="is_redirector(item)"
             name="${r_id}" target_url="${item.target_url}" />
    </metal:chunk>
   </tal:loop>
  </section>
 </sections>
</peopledirectory>
"""

def _xxx_category_items(category):
    if 'data' in category.__dict__:
        return category.items()
    return category._container.items()

def _xxx_column_info(section):
    result = []
    columns = getattr(section, 'columns', ())
    for i, column in enumerate(columns):
        name = getattr(column, '__name__', None)
        if name is None:
            name = 'column_%09d' % (i+1)
        result.append((name, column))
    return result

def _xxx_report_items(container):
    if 'order' in container.__dict__:
        return container.items()
    if 'reports' not in container.__dict__:
        return container.items()
    result = []
    for i, report in enumerate(container.reports):
        name = getattr(report, '__name__', None)
        if name is None:
            name = 'item_%09d' % (i+1)
        result.append((name, report))
    return result

def _xxx_report_filter_items(report):
    if 'filters' in report.__dict__:
        # Old-skool
        for key, values in report.filters.items():
            yield {'name': key,
                   'type': 'category',
                   'values': ' '.join(values),
                  }
    #return [(name, filter.values) for name, filter in report.items()]
    else:
        for name, obj in sorted(report.items()):
            info = {'name': name, 'type': 'unknown', 'obj': obj}
            if IPeopleReportCategoryFilter.providedBy(obj):
                info['type'] = 'category'
                info['values'] = ' '.join(obj.values)
            elif IPeopleReportGroupFilter.providedBy(obj):
                info['type'] = 'groups'
                info['values'] = ' '.join(obj.values)
            elif IPeopleReportIsStaffFilter.providedBy(obj):
                info['type'] = 'is_staff'
                info['include_staff'] = str(obj.include_staff)
            yield info

def dump_peopledir(peopledir):
    old_style = getattr(peopledir, 'categories', None) is not None
    template = PageTemplate(body=_DUMP_XML)
    if old_style:
        categories = peopledir.categories
    else:
        categories = peopledir['categories']
    return template(peopledir=peopledir,
                    categories=categories,
                    sections=[(x, peopledir[x]) for x in peopledir.order],
                    is_column=IPeopleSectionColumn.providedBy,
                    is_group=IPeopleReportGroup.providedBy,
                    is_report=IPeopleReport.providedBy,
                    is_redirector=IPeopleRedirector.providedBy,
                    category_items=_xxx_category_items,
                    acl_info=_acl_info,
                    column_info=_xxx_column_info,
                    report_items=_xxx_report_items,
                    report_filter_items=_xxx_report_filter_items,
                   )

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

def name_and_title(elem):
    name = elem.get('name')
    if name is None:
        name = elem.get('id')
    if name is None:
        raise ParseError("Missing name attribute (no ID, either)", elem)
    title = elem.get('title', name)
    return name, title

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
            permissions = []
            for p in e:
                if p.tag == 'permission':
                    permissions.append(p.text)
            if not permissions:
                raise ParseError("Missing permissions", e)
            if e.tag == 'allow':
                ace = (Allow, principal, tuple(permissions))
            else:
                ace = (Deny, principal, tuple(permissions))
        elif e.tag == 'no-inherit':
            ace = NO_INHERIT
        else:
            raise ParseError("Unrecognized element", e)
        acl.append(ace)
    obj.__acl__ = acl


def parse_report(people, elem):
    from karl.views.peopledirectory import COLUMNS
    name, title = name_and_title(elem)
    link_title = elem.get('link-title', title)
    css_class = elem.get('class', 'general')
    report = PeopleReport(title, link_title, css_class)

    categories = people.get('categories', {})
    for e in elem.findall('filter'):
        f_name = e.get('name')
        typ = e.get('type')
        values = e.get('values', '').split()
        if typ in ('category', 'groups') and not values:
            raise ParseError("No values given", e)
        if typ == 'category':
            category = e.get('category')
            if category is None:
                raise ParseError("No category given", e)
            pc = categories.get(category)
            if pc is None:
                raise ParseError("No such category defined", e)
            for v in values:
                if v not in pc:
                    raise ParseError("No such category value: %s" % v, e)
            report[category] = PeopleReportCategoryFilter(tuple(values))
        elif typ == 'groups':
            report[f_name] = PeopleReportGroupFilter(tuple(values))
        elif typ == 'is_staff':
            include_staff = report.get('include_staff', False)
            report[f_name] = PeopleReportIsStaffFilter(include_staff)
        else:
            raise ParseError("Unknown filter type", e)

    mlist_elem = elem.find('mailinglist')
    if mlist_elem is not None:
        mlist = report['mailinglist'] = PeopleReportMailingList()
        short_address = mlist_elem.get('short_address')
        if short_address is not None:
            if short_address in find_site(people).list_aliases:
                raise ParseError("Duplicate short address: %s" % short_address,
                                 mlist_elem)
            mlist.short_address = short_address

    columns = None
    e = elem.find('columns')
    if e is not None:
        columns = e.get('names', '').split()
    if not columns:
        columns = e.get('ids', '').split() # BBB
    if not columns:
        raise ParseError("No columns given", elem)
    for colid in columns:
        if not colid in COLUMNS:
            raise ParseError("No such column defined: %s" % colid, e)
    report.columns = tuple(columns)

    return name, report


def parse_report_group(people, elem):
    name, title = name_and_title(elem)
    group = PeopleReportGroup(title)
    sub_order = []
    for sub_name, sub in parse_reports(people, elem):
        group[sub_name] = sub
        sub_order.append(sub_name)
    group.order = tuple(sub_order)
    return name, group


def parse_reports(people, parent_elem):
    items = []
    names = set()
    for e in parent_elem:
        if isinstance(e, etree._Comment):
            continue
        if e.tag == 'report-group':
            name, group = parse_report_group(people, e)
            if name in names:
                raise ParseError('Duplicate name', e)
            items.append((name, group))
            names.add(name)
        elif e.tag == 'report':
            name, report = parse_report(people, e)
            if name in names:
                raise ParseError('Duplicate name', e)
            items.append((name, report))
            names.add(name)
        else:
            raise ParseError('Unrecognized element', e)
    return items

def parse_section(people, section_elem):
    items = []
    for e in section_elem:
        if e.tag == 'report':
            name, report = parse_report(people, e)
            items.append((name, report))
        elif e.tag == 'report-group':
            name, group = parse_report_group(people, e)
            items.append((name, group))
        elif e.tag == 'column':
            name, _ = name_and_title(e)
            column = PeopleSectionColumn()
            c_order = []
            for sub_name, sub in parse_reports(people, e):
                column[sub_name] = sub
                c_order.append(sub_name)
            column.order = tuple(c_order)
            items.append((name, column))
        elif e.tag == 'redirector':
            name, _ = name_and_title(e)
            redirector = PeopleRedirector()
            redirector.target_url = e.get('target_url')
            items.append((name, redirector))
        elif e.tag == 'acl':
            pass  # section ACL is set by caller
        else:
            raise ParseError('Unrecognized element', e)
    return items


def clear_mailinglist_aliases(peopledir):
    site = find_site(peopledir)
    aliases = site.list_aliases
    pd_path = resource_path(peopledir)
    for k, v in list(aliases.items()): # avoid mutating-while-iterating
        if v.startswith(pd_path):
            del aliases[k]


def find_mailinglist_aliases(peopledir):

    def _walk_mailinglists(container, mailinglists=None):
        if mailinglists is None:
            mailinglists = []
        if IPeopleReportMailingList.providedBy(container):
            mailinglists.append(container)
        values = getattr(container, 'values', lambda: ())
        if callable(values):
            for v in values():
                _walk_mailinglists(v, mailinglists)
        return mailinglists

    site = find_site(peopledir)
    aliases = site.list_aliases
    for mailinglist in _walk_mailinglists(peopledir):
        short_address = mailinglist.short_address
        if short_address in aliases:
            raise ValueError('Duplicate short_address: %s' % short_address)
        aliases[short_address] = resource_path(mailinglist.__parent__)


def peopleconf(peopledir, tree, force_reindex=False):
    # tree is an lxml.etree element.
    if tree.find('categories') is not None:
        try:
            del peopledir.categories
        except AttributeError:  # already scrubbed
            pass
        categories = peopledir.get('categories')
        if not isinstance(categories, PeopleCategories):
            if 'categories' in peopledir:
                del peopledir['categories']
            categories = peopledir['categories'] = PeopleCategories()
        doomed = list(categories.keys())
        for x in doomed:
            del categories[x]
        for cat_elem in tree.findall('categories/category'):
            c_name, title = name_and_title(cat_elem)
            pc = categories[c_name] = PeopleCategory(title)
            for value_elem in cat_elem.findall('value'):
                v_name, title = name_and_title(value_elem)
                # get the content of the description as XML
                # Note that lxml.etree.Element.text is documented as the
                # "text before the first subelement".
                text = value_elem.text or ''
                description = text + u''.join(
                    etree.tostring(e, encoding=unicode) for e in value_elem)
                item = PeopleCategoryItem(title, description.strip())
                pc[v_name] = item

    for name in list(peopledir.keys()):
        if name != 'categories':
            del peopledir[name]

    clear_mailinglist_aliases(peopledir)

    section_order = []
    for section_elem in tree.findall('sections/section'):
        name, title = name_and_title(section_elem)
        section_order.append(name)
        tab_title = section_elem.get('tab-title', title)
        section = peopledir[name] = PeopleSection(title, tab_title)
        set_acl(section, section_elem)

        sub_order = []
        for sub_name, sub in parse_section(peopledir, section_elem):
            section[sub_name] = sub
            sub_order.append(sub_name)
        section.order = tuple(sub_order)

    find_mailinglist_aliases(peopledir)

    # 'categories' never in the order.
    peopledir.order = section_order

    need_reindex = peopledir.update_indexes()
    if need_reindex or force_reindex:
        reindex_peopledirectory(peopledir)
