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

import math
import re
from simplejson import JSONEncoder

from webob.exc import HTTPFound
from webob.exc import HTTPBadRequest
from webob import Response

from zope.component import getMultiAdapter

from repoze.bfg.chameleon_zpt import render_template_to_response
from repoze.bfg.traversal import model_path
from repoze.bfg.traversal import find_model
from repoze.bfg.security import authenticated_userid
from repoze.bfg.security import has_permission
from repoze.bfg.url import model_url

from karl.models.interfaces import ITagQuery

from karl.utils import find_catalog
from karl.utils import find_profiles
from karl.utils import find_tags
from karl.utils import get_content_type_name
from karl.utils import get_setting

from karl.views.api import TemplateAPI


def get_tags_client_data(context, request):
    """
    Gets the client data for the tags field.

    When used, the data needs to be injected to the templates::

        head_data=convert_to_script(dict(
            tags_field = get_tags_client_data(context, request),
            # ... data for more widgets
            # ...
            ))

    """
    # provide client data for rendering current tags in the tagbox.
    tagquery = getMultiAdapter((context, request), ITagQuery)
    tags_field = dict(
        records = tagquery.tagswithcounts,
        docid = tagquery.docid,
        )
    return tags_field


def add_tags(context, request, values):
    """ Add the specified tags.

    o Existing tags remain assigned.
    """
    if values:
        if isinstance(values, basestring):
            values = [values]
        path = model_path(context)
        catalog = find_catalog(context)
        docid = catalog.document_map.docid_for_address(path)
        username = authenticated_userid(request)
        tags = find_tags(context)
        if tags is not None: # testing
            new = list(tags.getTags(items=(docid,), users=(username,)))
            new.extend(values)
            tags.update(item=docid, user=username, tags=new)

def del_tags(context, request, values):
    """ Delete the specified tags.
    """
    username = authenticated_userid(request)
    path = model_path(context)
    catalog = find_catalog(context)
    docid = catalog.document_map.docid_for_address(path)
    tags = find_tags(context)
    for tag in values:
        tags.delete(item=docid, user=username, tag=tag)

def set_tags(context, request, values):
    """ Set the specified tags, previously removing any existing tags.
    """
    if values is None:
        values = ()
    username = authenticated_userid(request)
    path = model_path(context)
    catalog = find_catalog(context)
    docid = catalog.document_map.docid_for_address(path)
    tags = find_tags(context)
    if tags is not None: # testing
        tags.update(item=docid, user=username, tags=values)


def jquery_tag_search_view(context, request):
    tag_query_tool = getMultiAdapter((context, request), ITagQuery)
    # case insensitive
    prefix = request.params['val'].lower()
    values = tag_query_tool.tags_with_prefix(prefix)
    records = [dict(text=value) for value in values]
    result = JSONEncoder().encode(records)
    return Response(result, content_type="application/x-json")

re_tag = re.compile(r'^[a-zA-Z0-9\.\-_]+$')

def _validate_tag(tag):
    return re_tag.match(tag)

def jquery_tag_add_view(context, request):
    value = request.params['val'].strip()
    value = value.decode('utf')
    add_tags(context, request, [value])
    status = {}
    # check for valid characters
    if not _validate_tag(value):
        # This will signal an error for the client.
        status['error'] = 'Adding tag failed, it contains illegal characters.'
    result = JSONEncoder().encode(status)
    return Response(result, content_type="application/x-json")

def jquery_tag_del_view(context, request):
    value = request.params['val'].strip()
    value = value.decode('utf')
    del_tags(context, request, [value])
    status = {}
    result = JSONEncoder().encode(status)
    return Response(result, content_type="application/x-json")

def showtag_view(context, request, template='templates/showtag.pt',
                 community=None, user=None, crumb_title=None, ):
    """Show a page for a particular tag, optionally refined by context."""

    page_title = 'Show Tag'
    api = TemplateAPI(context, request, page_title)

    # The tag screens (cloud, listing, and this view) each have a
    # "jump box" that allows you to quickly jump to another tag.  All
    # three will point here at /showtag?tag=tag1.  We detect this mode
    # and do a redirect.
    jump_tag = request.params.get('jumptag', False)
    if jump_tag:
        location = model_url(context, request, request.view_name, jump_tag)
        return HTTPFound(location=location)

    # Our strategy is to support tag URLs that are like this:
    #     /showtag/tag1
    # ...instead of:
    #     /tagpage.html?tag=tag1
    # However, our tag data isn't traversable (it is site.tags and not
    # site['tags'].  So we have a view at /showtag that picks apart
    # the next hop in the URL.
    tag = request.subpath
    if not tag:
        # The user didn't provide anything beyond /showtag in the URL
        tag = None
        entries = related = []
    else:
        # Ahh, the good part.  Let's find some tag results and unpack
        # data into what the ZPT needs.
        tag = tag[0]
        page_title = 'Show Tag ' + tag

        catalog = find_catalog(context)
        dm = catalog.document_map
        tags = find_tags(context)
        related = tags.getRelatedTags(tag, user=user, community=community)
        entries = []
        if user:
            users = (user,)
        else:
            users = None
        for docid in tags.getItems(tags=(tag,), users=users,
                                   community=community,
                                   ):
            # XXX Need to wire in batching
            address = dm.address_for_docid(int(docid))
            if address is None:
                raise KeyError(docid)
            resource = find_model(context, address)

            # Skip documents which aren't viewable by authenticated user
            if not has_permission('view', resource, request):
                continue

            # Do a secondary query for each result to find the
            # per-user info
            users = tags.getUsers(tags=(tag,), items=(docid,),
                                  community=community)
            if len(users) == 1:
                tuh = '1 person'
            else:
                tuh = '%s people' % len(users)

            tuhref = model_url(context, request, 'tagusers.html',
                               query={'tag': tag, 'docid': docid})
            entry = {
                'title': resource.title,
                'description': getattr(resource, 'description', ''),
                'href': model_url(resource, request),
                'type': get_content_type_name(resource),
                'tagusers_href': tuhref,
                'tagusers_count': tuh,
                }
            entries.append(entry)

    args = dict(
        api=api,
        tag=tag,
        entries=entries,
        related=related,
    )

    if crumb_title:
        # XXX Would context.title be a bit nicer for displaying to user?
        system_name = get_setting(context, 'system_name', 'KARL')
        args['crumbs'] = '%s / %s / %s' % (
            system_name, crumb_title, context.__name__)

    return render_template_to_response(template, **args)

def community_showtag_view(context, request):
    """Show a page for a particular community tag."""
    return showtag_view(context, request,
                        template='templates/community_showtag.pt',
                        community=context.__name__,
                        crumb_title='Communities')

def profile_showtag_view(context, request):
    """Show a page for a particular user tag."""
    return showtag_view(context, request,
                        template='templates/profile_showtag.pt',
                        user=context.__name__,
                        crumb_title='Profiles')

def norm(factor, stddev):
    if factor >= 2 * stddev:
        weight = 7
    elif factor >= stddev:
        weight = 6
    elif factor >= 0.5 * stddev:
        weight = 5
    elif factor > -0.5 * stddev:
        weight = 4
    elif factor > -stddev:
        weight = 3
    elif factor > -2 * stddev:
        weight = 2
    else:
        weight = 1
    return weight

def _calculateTagWeights(taglist):
    if not taglist:
        return taglist
    counts = list()
    for tag in taglist:
        counts.append(tag['count'])
    count = len(taglist)
    total = reduce(lambda x, y: x+ y, counts)
    mean = total/count
    var = reduce(lambda x,y: x + math.pow(y-mean, 2), counts, 0)/count
    stddev = math.sqrt(var)
    tmp = {}
    for t in taglist:
        factor = (t['count'] - mean)
        weight = t['weight'] = norm(factor, stddev)
        t['class'] = 'tagweight%d' % weight
    return taglist

def tag_cloud_view(context, request):
    page_title = 'Tag Cloud'
    api = TemplateAPI(context, request, page_title)
    tags = find_tags(context)
    if tags is not None:
        cloud = [{'name': x[0], 'count': x[1]} for x in tags.getCloud()]
        limited = list(reversed(sorted(cloud, key=lambda x: x['count']))
                      )[:100]
        entries = sorted(_calculateTagWeights(limited),
                         key=lambda x: x['name'])
    else:
        entries = ()

    return render_template_to_response(
        'templates/tagcloud.pt',
        api=api,
        entries=entries,
        )

def community_tag_cloud_view(context, request):
    page_title = 'Tag Cloud'
    api = TemplateAPI(context, request, page_title)
    tags = find_tags(context)
    if tags is not None:
        cloud = [{'name': x[0], 'count': x[1]}
                    for x in tags.getCloud(community=context.__name__)]
        limited = list(reversed(sorted(cloud, key=lambda x: x['count']))
                      )[:100]
        entries = sorted(_calculateTagWeights(limited),
                         key=lambda x: x['name'])
    else:
        entries = ()

    system_name = get_setting(context, 'system_name', 'KARL')
    return render_template_to_response(
        'templates/community_tagcloud.pt',
        api=api,
        entries=entries,
        crumbs='%s / Communities / %s' % (system_name, context.__name__),
        )


def tag_listing_view(context, request):
    page_title = 'Tag Listing'
    api = TemplateAPI(context, request, page_title)
    tags = find_tags(context)

    if tags is None:
        entries = ()
    else:
        entries = [{'name': x[0], 'count': x[1]} for x in tags.getFrequency()]
        entries.sort(key=lambda x: x['name'])

    return render_template_to_response(
        'templates/taglisting.pt',
        api=api,
        entries=entries,
        )


def community_tag_listing_view(context, request):
    page_title = 'Tag Listing'
    api = TemplateAPI(context, request, page_title)
    tags = find_tags(context)

    if tags is None:
        entries = ()
    else:
        entries = [{'name': x[0], 'count': x[1]}
                        for x in tags.getFrequency(community=context.__name__)]
        entries.sort(key=lambda x: x['name'])

    system_name = get_setting(context, 'system_name', 'KARL')
    return render_template_to_response(
        'templates/community_taglisting.pt',
        api=api,
        entries=entries,
        crumbs='%s / Communities / %s' % (system_name, context.__name__),
        )


def profile_tag_listing_view(context, request):
    page_title = 'Tag Listing'
    api = TemplateAPI(context, request, page_title)
    tags = find_tags(context)

    if tags is None:
        entries = ()
    else:
        names = tags.getTags(users=(context.__name__,))
        entries = [{'name': x[0], 'count': x[1]}
                        for x in tags.getFrequency(names,
                                                   user=context.__name__)]
        entries.sort(key=lambda x: x['name'])

    system_name = get_setting(context, 'system_name', 'KARL')
    return render_template_to_response(
        'templates/profile_taglisting.pt',
        api=api,
        entries=entries,
        crumbs='%s / Profiles / %s' % (system_name, context.__name__),
        )

def tag_users_view(context, request):
    page_title = 'Tag Users'
    api = TemplateAPI(context, request, page_title)

    tag = request.params.get('tag', None)
    docid = request.params.get('docid', None)
    # Test for some cases
    if tag is None:
        return HTTPBadRequest('Missing parameter for tag')
    if docid is None:
        return HTTPBadRequest('Missing parameter for docid')

    docid = int(docid)
    tags = find_tags(context)
    profiles = find_profiles(context)
    catalog = find_catalog(context)
    address = catalog.document_map.address_for_docid(docid)
    target = find_model(context, address)
    if tags is not None and profiles is not None:
        users = []
        for userid in tags.getUsers(tags=[tag], items=[docid]):
            profile = profiles[userid]
            fullname = profile.firstname + ' ' + profile.lastname
            also = [x for x in tags.getTags(items=[docid], users=[userid])
                         if x != tag]
            users.append({'login': userid,
                          'fullname': fullname,
                          'also': also,
                         })

    else:
        users = ()

    return render_template_to_response(
        'templates/tagusers.pt',
        api=api,
        tag=tag,
        url=model_url(target, request),
        title=target.title,
        users=users,
        )

def community_tag_users_view(context, request):
    page_title = 'Tag Users'
    api = TemplateAPI(context, request, page_title)

    tag = request.params.get('tag', None)
    docid = request.params.get('docid', None)
    # Test for some cases
    if tag is None:
        return HTTPBadRequest('Missing parameter for tag')
    if docid is None:
        return HTTPBadRequest('Missing parameter for docid')

    docid = int(docid)
    tags = find_tags(context)
    profiles = find_profiles(context)
    catalog = find_catalog(context)
    address = catalog.document_map.address_for_docid(docid)
    target = find_model(context, address)
    if tags is not None and profiles is not None:
        users = []
        for userid in tags.getUsers(tags=[tag], items=[docid],
                                    community=context.__name__):
            profile = profiles[userid]
            fullname = profile.firstname + ' ' + profile.lastname
            also = [x for x in tags.getTags(items=[docid], users=[userid],
                                            community=context.__name__)
                         if x != tag]
            users.append({'login': userid,
                          'fullname': fullname,
                          'also': also,
                         })

    else:
        users = ()

    return render_template_to_response(
        'templates/community_tagusers.pt',
        api=api,
        tag=tag,
        url=model_url(target, request),
        title=target.title,
        users=users,
        )


re_tag = re.compile(r"^[a-zA-Z0-9\.\-_]+$")

def manage_tags_view(context, request):
    page_title = 'Manage Tags'
    api = TemplateAPI(context, request, page_title)
    tagger = find_tags(context)
    userid = context.__name__
    error = ''
    old = ''
    new = ''

    if 'form.rename' in request.POST:
        old_tag = request.POST['old_tag']
        new_tag = request.POST['new_tag']
        # check that tag contains only valid characters
        if re_tag.match(new_tag) is None:
            error = u'Value contains characters that are not allowed in a tag.'
            old = old_tag
            new = new_tag
        else:
            docids = tagger.getItems(tags=[old_tag], users=[userid])
            to_update = {}
            for tagob in tagger.getTagObjects(items=docids, users=[userid]):
                if tagob.name == old_tag:
                    name = new_tag
                else:
                    name = tagob.name
                to_update.setdefault(tagob.item, []).append(name)
            for docid in docids:
                tagger.update(item=docid, user=userid,
                              tags=to_update.get(docid, []))

    if 'form.delete' in request.POST:
        old_tag = request.POST['old_tag']
        for docid in tagger.getItems(tags=[old_tag], users=[userid]):
            tagger.delete(item=docid, user=userid, tag=old_tag)

    if tagger is None:
        tags = ()
    else:
        tags = list(tagger.getTags(users=(context.__name__,)))
        tags.sort()

    return render_template_to_response(
        'templates/profile_tagedit.pt',
        api=api,
        tags=tags,
        error=error,
        old=old,
        new=new,
        )
