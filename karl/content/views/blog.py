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

import calendar
import datetime

from webob.exc import HTTPFound
from formencode import Invalid
from zope.component.event import objectEventNotify
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.component import queryUtility
from zope.interface import implements

from repoze.bfg.chameleon_zpt import render_template
from repoze.bfg.chameleon_zpt import render_template_to_response
from repoze.bfg.chameleon_zpt import get_template
from repoze.bfg.security import authenticated_userid
from repoze.bfg.security import has_permission
from repoze.bfg.url import model_url
from repoze.workflow import get_workflow
from repoze.lemonade.content import create_content
from repoze.enformed import FormSchema

from karl.content.interfaces import IBlog
from karl.content.interfaces import IBlogEntry
from karl.content.views.interfaces import IBylineInfo
from karl.content.views.utils import extract_description
from karl.content.views.utils import store_attachments
from karl.content.views.utils import fetch_attachments
from karl.events import ObjectModifiedEvent
from karl.events import ObjectWillBeModifiedEvent
from karl.security.workflow import get_security_states
from karl.utilities.alerts import Alerts
from karl.utilities.interfaces import IAlerts
from karl.utilities.interfaces import IKarlDates
from karl.utils import find_interface
from karl.utils import find_profiles
from karl.utils import get_setting
from karl.utils import coarse_datetime_repr
from karl.views import baseforms
from karl.views.api import TemplateAPI
from karl.views.form import render_form_to_response
from karl.views.interfaces import ISidebar
from karl.views.tags import set_tags
from karl.views.tags import get_tags_client_data
from karl.views.utils import convert_to_script
from karl.views.utils import make_unique_name
from karl.views.utils import templates_formfields_path
from karl.views.batch import get_container_batch
from karl.views.baseforms import security_state as security_state_field

def show_blog_view(context, request):

    if 'year' in request.GET and 'month' in request.GET:
        year = int(request.GET['year'])
        month = int(request.GET['month'])
        def filter_func(name, item):
            created = item.created
            return created.year == year and created.month == month
        dt = datetime.date(year, month, 1).strftime('%B %Y')
        page_title = 'Blog: %s' % dt
    else:
        filter_func = None
        page_title = 'Blog'

    api = TemplateAPI(context, request, page_title)

    actions = []
    if has_permission('create', context, request):
        actions.append(
            ('Add Blog Entry', 'add_blogentry.html'),
            )

    batch = get_container_batch(
        context, request, filter_func=filter_func, interfaces=[IBlogEntry],
        sort_index='creation_date', reverse=True)

    # Unpack into data for the emplate
    entries = []
    profiles = find_profiles(context)
    karldates = getUtility(IKarlDates)
    fmt0 = '<a href="%s#addcomment">Add a Comment</a>'
    fmt1 = '<a href="%s#comments">1 Comment</a>'
    fmt2 = '<a href="%s#comments">%i Comments</a>'

    for entry in batch['entries']:
        profile = profiles[entry.creator]
        byline_info = getMultiAdapter((entry, request), IBylineInfo)
        entry_url = model_url(entry, request)

        # Get information about comments on this entry to display in
        # the last line of the entry
        comment_count = len(entry['comments'])
        if comment_count == 0:
            comments_blurb = fmt0 % entry_url
        elif comment_count == 1:
            comments_blurb = fmt1 % entry_url
        else:
            comments_blurb = fmt2 % (entry_url, comment_count)
        info = {
            'title': entry.title,
            'href': model_url(entry, request),
            'description': entry.description,
            'creator_title': profile.title,
            'creator_href': entry_url,
            'long_date': karldates(entry.created, 'longform'),
            'byline_info': byline_info,
            'comments_blurb': comments_blurb,
            }
        entries.append(info)

    system_email_domain = get_setting(context, "system_email_domain")
    feed_url = "%satom.xml" % model_url(context, request)
    workflow = get_workflow(IBlogEntry, 'security', context)
    security_states = get_security_states(workflow, None, request)

    return render_template_to_response(
        'templates/show_blog.pt',
        api=api,
        actions=actions,
        entries=entries,
        system_email_domain=system_email_domain,
        feed_url=feed_url,
        batch_info = batch,
        security_states=security_states,
        )


def show_blogentry_view(context, request):

    post_url = model_url(context, request, "comments", "add_comment.html")
    karldates = getUtility(IKarlDates)
    profiles = find_profiles(context)
    workflow = get_workflow(IBlogEntry, 'security', context)

    if workflow is None:
        security_states = []
    else:
        security_states = get_security_states(workflow, context, request)

    # Convert blog comments into a digestable form for the template
    comments = []

    page_title = context.title
    api = TemplateAPI(context, request, page_title)
    for comment in context['comments'].values():
        profile = profiles.get(comment.creator)
        author_name = profile.title
        author_url = model_url(profile, request)

        newc = {}
        newc['id'] = comment.__name__
        if has_permission('edit', comment, request):
            newc['edit_url'] = model_url(comment, request, 'edit.html')
        else:
            newc['edit_url'] = None

        if has_permission('delete', comment, request):
            newc['delete_url'] = model_url(comment, request, 'delete.html')
        else:
            newc['delete_url'] = None

        # Display portrait
        photo = profile.get_photo()
        photo_url = {}
        if photo is not None:
            photo_url = model_url(photo, request)
        else:
            photo_url = api.static_url + "/images/defaultUser.gif"
        newc["portrait_url"] = photo_url

        newc['author_url'] = author_url
        newc['author_name'] = author_name

        newc['date'] = karldates(comment.created, 'longform')
        newc['timestamp'] = comment.created
        newc['text'] = comment.text

        # Fetch the attachments info
        newc['attachments'] = fetch_attachments(comment, request)
        comments.append(newc)
    comments.sort(key=lambda c: c['timestamp'])

    client_json_data = dict(
        tagbox = get_tags_client_data(context, request),
        )

    actions = []
    if has_permission('edit', context, request):
        actions.append(('Edit', 'edit.html'))
    if has_permission('edit', context, request):
        actions.append(('Delete', 'delete.html'))

    api.is_taggable = True

    byline_info = getMultiAdapter((context, request), IBylineInfo)
    blog = find_interface(context, IBlog)
    backto = {
        'href': model_url(blog, request),
        'title': blog.title,
        }

    return render_template_to_response(
        'templates/show_blogentry.pt',
        api=api,
        actions=actions,
        comments=comments,
        attachments=fetch_attachments(context['attachments'], request),
        head_data=convert_to_script(client_json_data),
        formfields=api.formfields,
        post_url=post_url,
        byline_info=byline_info,
        backto=backto,
        security_states = security_states,
        )


def add_blogentry_view(context, request):

    fieldwidgets = get_template(templates_formfields_path)
    tags_list=request.POST.getall('tags')
    form = AddBlogEntryForm(tags_list = tags_list)
    workflow = get_workflow(IBlogEntry, 'security', context)

    if workflow is None:
        security_states = []
    else:
        security_states = get_security_states(workflow, None, request)

    if security_states:
        form.add_field('security_state', security_state_field)

    if 'form.cancel' in request.POST:
        return HTTPFound(location=model_url(context, request))

    if 'form.submitted' in request.POST:
        try:
            converted = form.validate(request.POST)

            name = make_unique_name(context, converted['title'])

            creator = authenticated_userid(request)

            blogentry = create_content(IBlogEntry,
                converted['title'],
                converted['text'],
                extract_description(converted['text']),
                creator,
                )

            context[name] = blogentry

            # Set up workflow
            if workflow is not None:
                workflow.initialize(blogentry)
                if 'security_state' in converted:
                    workflow.transition_to_state(blogentry, request,
                                                 converted['security_state'])

            # Tags, attachments, alerts
            set_tags(blogentry, request, converted['tags'])
            store_attachments(blogentry['attachments'],
                              request.params, creator)
            if converted['sendalert']:
                alerts = queryUtility(IAlerts, default=Alerts())
                alerts.emit(blogentry, request)

            location = model_url(blogentry, request)
            return HTTPFound(location=location)

        except Invalid, e:
            fielderrors = e.error_dict
            fill_values = form.convert(request.POST)
    else:
        fielderrors = {}
        if workflow is None:
            fill_values = {'security_state':''}
        else:
            fill_values = {'security_state':workflow.initial_state}

    # provide client data for rendering current tags in the tagbox.
    if 'form.submitted' in request.POST:
        # We arrived here because the form is invalid.
        tagbox_records = [dict(tag=tag) for tag in request.POST.getall('tags')]
    else:
        # Since this is a new entry, we start with no tags.
        tagbox_records = []

    client_json_data = convert_to_script(dict(
        tags_field = dict(
            # There is no document right now, so we leave docid empty.
            # This will cause the count links become non-clickable.
            records = tagbox_records,
            ),
    ))

    # Render the form and shove some default values in
    page_title = 'Add Blog Entry'
    api = TemplateAPI(context, request, page_title)

    return render_form_to_response(
        'templates/add_blogentry.pt',
        form,
        fill_values,
        post_url=request.url,
        formfields=fieldwidgets,
        fielderrors=fielderrors,
        api=api,
        form=form,
        head_data=client_json_data,
        security_states = security_states,
        )

def edit_blogentry_view(context, request):

    tags_list = request.POST.getall('tags')
    form = EditBlogEntryForm(tags_list=tags_list)
    workflow = get_workflow(IBlogEntry, 'security', context)

    if workflow is None:
        security_states = []
    else:
        security_states = get_security_states(workflow, context, request)

    if security_states:
        form.add_field('security_state', security_state_field)

    if 'form.cancel' in request.POST:
        return HTTPFound(location=model_url(context, request))

    if 'form.submitted' in request.POST:
        try:
            converted = form.validate(request.POST)
            # *will be* modified event
            objectEventNotify(ObjectWillBeModifiedEvent(context))
            if 'security_state' in converted:
                if workflow is not None:
                    workflow.transition_to_state(context, request,
                                                 converted['security_state'])

            context.title = converted['title']
            context.text = converted['text']
            context.description = extract_description(converted['text'])

            # Save the attachments
            # This is handled out of the form
            attachments = []
            for key, value in request.params.iteritems():
                if key.startswith('attachment') and value != '':
                    attachments.append(value)

            # Tags and attachments
            set_tags(context, request, converted['tags'])
            store_attachments(context['attachments'],
                              request.params, authenticated_userid(request))

            # modified
            context.modified_by = authenticated_userid(request)
            objectEventNotify(ObjectModifiedEvent(context))

            location = model_url(context, request)
            return HTTPFound(location=location)

        except Invalid, e:
            fielderrors = e.error_dict
            fill_values = form.convert(request.POST)
    else:
        fielderrors = {}
        if workflow is None:
            security_state = ''
        else:
            security_state = workflow.state_of(context)
        fill_values = dict(
            title=context.title,
            text=context.text,
            security_state = security_state,
            )

   # prepare client data
    client_json_data = dict(
        tags_field = get_tags_client_data(context, request),
        )

    # Render the form and shove some default values in
    page_title = 'Edit ' + context.title
    api = TemplateAPI(context, request, page_title)

    return render_form_to_response(
        'templates/edit_blogentry.pt',
        form,
        fill_values,
        post_url=request.url,
        formfields=api.formfields,
        fielderrors=fielderrors,
        api=api,
        head_data=convert_to_script(client_json_data),
        security_states = security_states,
        )

class AddBlogEntryForm(FormSchema):
    title = baseforms.title
    text = baseforms.text
    tags = baseforms.tags
    sendalert = baseforms.sendalert

class EditBlogEntryForm(FormSchema):
    title = baseforms.title
    tags = baseforms.tags
    text = baseforms.text
    sendalert = baseforms.sendalert

def coarse_month_range(year, month):
    """Returns the range of coarse datetimes for a month."""
    last_day = calendar.monthrange(year, month)[1]
    first_moment = coarse_datetime_repr(
        datetime.datetime(year, month, 1))
    last_moment = coarse_datetime_repr(
        datetime.datetime(year, month, last_day, 23, 59, 59))
    return first_moment, last_moment


class MonthlyActivity(object):

    def __init__(self, year, month, count):
        self.year = year
        self.month = month
        self.month_name = calendar.month_name[month]
        self.count = count


class BlogSidebar(object):
    implements(ISidebar)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, api):
        counts = {}  # {(year, month): count}
        for entry in self.context.values():
            if not IBlogEntry.providedBy(entry):
                continue
            if not has_permission('view', entry, self.request):
                continue
            year = entry.created.year
            month = entry.created.month
            counts[(year, month)] = counts.get((year, month), 0) + 1
        counts = counts.items()
        counts.sort()
        counts.reverse()
        activity_list = [MonthlyActivity(year, month, count)
            for ((year, month), count) in counts]
        blog_url = model_url(self.context, self.request)
        return render_template(
            'templates/blog_sidebar.pt',
            api=api,
            activity_list=activity_list,
            blog_url=blog_url,
            )
