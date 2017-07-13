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
import os

import formish
import schemaish
from validatish import validator
from schemaish.type import File as SchemaFile

from pyramid.httpexceptions import HTTPFound
from zope.component.event import objectEventNotify
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.component import queryUtility
from zope.interface import implements

from pyramid.renderers import render
from pyramid_formish import Form
from pyramid_formish.zcml import FormAction
from pyramid.security import authenticated_userid
from pyramid.security import effective_principals
from pyramid.security import has_permission
from pyramid.traversal import find_resource
from pyramid.url import resource_url
from repoze.workflow import get_workflow
from repoze.lemonade.content import create_content

from karl.content.interfaces import IBlog
from karl.content.interfaces import IBlogEntry
from karl.content.views.commenting import AddCommentFormController
from karl.content.views.interfaces import IBylineInfo
from karl.content.views.utils import extract_description
from karl.content.views.utils import fetch_attachments
from karl.content.views.utils import sendalert_default
from karl.content.views.utils import upload_attachments
from karl.events import ObjectModifiedEvent
from karl.events import ObjectWillBeModifiedEvent
from karl.models.newtqbe import qbe
from karl.security.workflow import get_security_states
from karl.utilities.alerts import Alerts
from karl.utilities.image import relocate_temp_images
from karl.utilities.image import thumb_url
from karl.utilities.interfaces import IAlerts
from karl.utilities.interfaces import IKarlDates
from karl.utils import find_catalog
from karl.utils import find_community
from karl.utils import find_interface
from karl.utils import find_profiles
from karl.utils import get_setting
from karl.utils import coarse_datetime_repr
from karl.views.api import TemplateAPI
from karl.views.interfaces import ISidebar
from karl.views.people import PROFILE_THUMB_SIZE
from karl.views.tags import set_tags
from karl.views.tags import get_tags_client_data
from karl.views.utils import convert_to_script
from karl.views.utils import make_unique_name

from karl.views.batch import get_simple_batch

from karl.views.forms import widgets as karlwidgets
from karl.views.forms.filestore import get_filestore

def show_blog_view(context, request):
    if 'year' in request.GET and 'month' in request.GET:
        year = int(request.GET['year'])
        month = int(request.GET['month'])
        dt = datetime.date(year, month, 1).strftime('%B %Y')
        page_title = 'Blog: %s' % dt
        where_month = (
            "and state->>'created' like '%.4d-%.2d%%%%'" % (year, month))
    else:
        page_title = 'Blog'
        where_month = ''

    from newt.db import search
    community = find_community(context)
    community_cond = qbe.sql(context._p_jar, dict(community=community))
    results = search.search(
        context._p_jar,
        """
        select * from newt natural join karlex where
        class_name = 'karl.content.models.blog.BlogEntry'
        and """ + community_cond + """
        and newt_can_view(state, %s)
        """ + where_month + """
        order by state->>'created' desc
        """,
        effective_principals(request),
        )

    api = TemplateAPI(context, request, page_title)

    actions = []
    if has_permission('create', context, request):
        actions.append(
            ('Add Blog Entry',
             request.resource_url(context, 'add_blogentry.html')),
            )

    batch = get_simple_batch(results, context, request)

    # Unpack into data for the template
    entries = []
    profiles = find_profiles(context)
    karldates = getUtility(IKarlDates)
    fmt0 = '<a href="%s#addcomment">Add a Comment</a>'
    fmt1 = '<a href="%s#comments">1 Comment</a>'
    fmt2 = '<a href="%s#comments">%i Comments</a>'

    for entry in batch['entries']:
        profile = profiles[entry.creator]
        byline_info = getMultiAdapter((entry, request), IBylineInfo)
        entry_url = resource_url(entry, request)

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
            'href': resource_url(entry, request),
            'description': entry.description,
            'creator_title': profile.title,
            'creator_href': entry_url,
            'long_date': karldates(entry.created, 'longform'),
            'byline_info': byline_info,
            'comments_blurb': comments_blurb,
            }
        entries.append(info)

    feed_url = "%satom.xml" % resource_url(context, request)
    workflow = get_workflow(IBlogEntry, 'security', context)
    if workflow is None:
        security_states = []
    else:
        security_states = get_security_states(workflow, None, request)

    system_email_domain = get_setting(context, "system_email_domain")
    return dict(
        api=api,
        actions=actions,
        entries=entries,
        system_email_domain=system_email_domain,
        feed_url=feed_url,
        batch_info = batch,
        security_states=security_states,
        )

def show_mailin_trace_blog(context, request):
    path = get_setting(context, 'mailin_trace_file')
    formatted_timestamp = None
    if os.path.exists(path):
        timestamp = os.path.getmtime(path)
        timestamp = datetime.datetime.fromtimestamp(timestamp)
        formatted_timestamp = timestamp.ctime()
    return dict(
        api=TemplateAPI(context, request),
        system_email_domain=get_setting(context, 'system_email_domain'),
        timestamp=formatted_timestamp,
    )

def redirect_to_add_form(context, request):
    return HTTPFound(
            location=resource_url(context, request, 'add_blogentry.html'))

def show_blogentry_view(context, request):

    post_url = resource_url(context, request, "comments", "add_comment.html")
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
        author_url = resource_url(profile, request)

        newc = {}
        newc['id'] = comment.__name__
        if has_permission('edit', comment, request):
            newc['edit_url'] = resource_url(comment, request, 'edit.html')
        else:
            newc['edit_url'] = None

        if has_permission('delete', comment, request):
            newc['delete_url'] = resource_url(comment, request, 'delete.html')
        else:
            newc['delete_url'] = None

        if has_permission('administer', comment, request):
            newc['advanced_url'] = resource_url(comment, request, 'advanced.html')
        else:
            newc['advanced_url'] = None

        # Display portrait
        photo = profile.get('photo')
        if photo is not None:
            photo_url = thumb_url(photo, request, PROFILE_THUMB_SIZE)
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
    if has_permission('administer', context, request):
        actions.append(('Advanced', 'advanced.html'))

    api.is_taggable = True

    byline_info = getMultiAdapter((context, request), IBylineInfo)
    blog = find_interface(context, IBlog)
    backto = {
        'href': resource_url(blog, request),
        'title': blog.title,
        }

    # manually construct formish comment form
    controller = AddCommentFormController(context['comments'], request)
    form_schema = schemaish.Structure()
    form_fields = controller.form_fields()
    for fieldname, field in form_fields:
        form_schema.add(fieldname, field)
    form_action_url = '%sadd_comment.html' % resource_url(context['comments'],
                                                       request)
    comment_form = Form(form_schema, add_default_action=False, name='save',
                        action_url=form_action_url)
    form_defaults = controller.form_defaults()
    comment_form.defaults = form_defaults
    request.form_defaults = form_defaults

    form_actions = [FormAction('submit', 'submit'),
                    FormAction('cancel', 'cancel', validate=False)]
    for action in form_actions:
        comment_form.add_action(action.name, action.title)

    widgets = controller.form_widgets(form_fields)
    for name, widget in widgets.items():
        comment_form[name].widget = widget

    # this is for enable imagedrawer for adding blog comments
    api.karl_client_data['text'] = dict(
            enable_imagedrawer_upload = True,
            )

    return dict(
        api=api,
        actions=actions,
        comments=comments,
        attachments=fetch_attachments(
            context['attachments'], request),
        head_data=convert_to_script(client_json_data),
        comment_form=comment_form,
        post_url=post_url,
        byline_info=byline_info,
        backto=backto,
        security_states = security_states,
        )


tags_field = schemaish.Sequence(schemaish.String())
text_field = schemaish.String()
sendalert_field = schemaish.Boolean(
    title='Send email alert to community members?')
security_field = schemaish.String(
    description=('Items marked as private can only be seen by '
                 'members of this community.'))
attachments_field = schemaish.Sequence(schemaish.File(),
                                       title='Attachments',
                                       )

class AddBlogEntryFormController(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.workflow = get_workflow(IBlogEntry, 'security', context)
        self.filestore = get_filestore(context, request, 'add-blogentry')

    def _get_security_states(self):
        return get_security_states(self.workflow, None, self.request)

    def form_defaults(self):
        defaults = {
            'title':'',
            'tags':[],
            'text':'',
            'attachments':[],
            'sendalert':sendalert_default(self.context,
                                          self.request),
            }
        if self.workflow is not None:
            defaults['security_state'] = self.workflow.initial_state
        return defaults

    def form_fields(self):
        fields = []
        title_field = schemaish.String(
            validator=validator.All(
                validator.Length(max=100),
                validator.Required(),
                )
            )
        fields.append(('title', title_field))
        fields.append(('tags', tags_field))
        fields.append(('text', text_field))
        fields.append(('attachments', attachments_field))
        fields.append(('sendalert', sendalert_field))
        security_states = self._get_security_states()
        if security_states:
            fields.append(('security_state', security_field))
        return fields

    def form_widgets(self, fields):
        widgets = {
            'title':formish.Input(empty=''),
            'tags':karlwidgets.TagsAddWidget(),
            'text':karlwidgets.RichTextWidget(empty=''),
            'attachments': karlwidgets.AttachmentsSequence(sortable=False,
                                                           min_start_fields=0),
            'attachments.*':karlwidgets.FileUpload2(filestore=self.filestore),
            'sendalert':karlwidgets.SendAlertCheckbox(),
            }
        schema = dict(fields)
        if 'security_state' in schema:
            security_states = self._get_security_states()
            widgets['security_state'] = formish.RadioChoice(
                options=[ (s['name'], s['title']) for s in security_states],
                none_option=None)
        return widgets


    def __call__(self):
        page_title = 'Add Blog Entry'
        api = TemplateAPI(self.context, self.request, page_title)
        api.karl_client_data['text'] = dict(
                enable_imagedrawer_upload = True,
                )
        return {'api':api, 'actions':()}

    def handle_cancel(self):
        return HTTPFound(location=resource_url(self.context, self.request))

    def handle_submit(self, converted):
        context = self.context
        request = self.request
        workflow = self.workflow
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

        # Tags, attachments, alerts, images
        set_tags(blogentry, request, converted['tags'])
        attachments_folder = blogentry['attachments']
        upload_attachments(filter(lambda x: x is not None,
                                  converted['attachments']),
                           attachments_folder,
                           creator, request)
        relocate_temp_images(blogentry, request)

        if converted['sendalert']:
            alerts = queryUtility(IAlerts, default=Alerts())
            alerts.emit(blogentry, request)

        location = resource_url(blogentry, request)
        self.filestore.clear()
        return HTTPFound(location=location)

class EditBlogEntryFormController(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.workflow = get_workflow(IBlogEntry, 'security', context)
        self.filestore = get_filestore(context, request, 'edit-blogentry')

    def _get_security_states(self):
        return get_security_states(self.workflow, None, self.request)

    def form_defaults(self):
        context = self.context
        attachments = [SchemaFile(None, x.__name__, x.mimetype)
                       for x in context['attachments'].values()]
        defaults = {
            'title':context.title,
            'tags':[], # initial values supplied by widget
            'text':context.text,
            'attachments':attachments,
            }
        if self.workflow is not None:
            defaults['security_state'] = self.workflow.state_of(context)
        return defaults

    def form_fields(self):
        fields = []
        title_field = schemaish.String(
            validator=validator.All(
                validator.Length(max=100),
                validator.Required(),
                )
            )
        fields.append(('title', title_field))
        fields.append(('tags', tags_field))
        fields.append(('text', text_field))
        fields.append(('attachments', attachments_field))
        security_states = self._get_security_states()
        if security_states:
            fields.append(('security_state', security_field))
        return fields

    def form_widgets(self, fields):
        tagdata = get_tags_client_data(self.context, self.request)
        widgets = {
            'title':formish.Input(empty=''),
            'tags':karlwidgets.TagsEditWidget(tagdata=tagdata),
            'text':karlwidgets.RichTextWidget(empty=''),
            'attachments': karlwidgets.AttachmentsSequence(sortable=False,
                                                           min_start_fields=0),
            'attachments.*':karlwidgets.FileUpload2(filestore=self.filestore),
             }
        security_states = self._get_security_states()
        schema = dict(fields)
        if 'security_state' in schema:
            security_states = self._get_security_states()
            widgets['security_state'] = formish.RadioChoice(
                options=[ (s['name'], s['title']) for s in security_states],
                none_option=None)
        return widgets

    def __call__(self):
        page_title = 'Edit ' + self.context.title
        api = TemplateAPI(self.context, self.request, page_title)
        api.karl_client_data['text'] = dict(
                enable_imagedrawer_upload = True,
                )
        return {'api':api, 'actions':()}

    def handle_cancel(self):
        return HTTPFound(location=resource_url(self.context, self.request))

    def handle_submit(self, converted):
        context = self.context
        request = self.request
        workflow = self.workflow
        # *will be* modified event
        objectEventNotify(ObjectWillBeModifiedEvent(context))
        if 'security_state' in converted:
            if workflow is not None:
                workflow.transition_to_state(context, request,
                                             converted['security_state'])

        context.title = converted['title']
        context.text = converted['text']
        context.description = extract_description(converted['text'])

        # Tags and attachments
        set_tags(context, request, converted['tags'])
        creator = authenticated_userid(request)
        attachments_folder = context['attachments']
        upload_attachments(
            filter(lambda x: x is not None, converted['attachments']),
            attachments_folder,
            creator, request)

        # modified
        context.modified_by = authenticated_userid(request)
        objectEventNotify(ObjectModifiedEvent(context))

        location = resource_url(context, request)
        self.filestore.clear()
        return HTTPFound(location=location)

def coarse_month_range(year, month):
    """Returns the range of coarse datetimes for a month."""
    last_day = calendar.monthrange(year, month)[1]
    first_moment = coarse_datetime_repr(
        datetime.datetime(year, month, 1))
    last_moment = coarse_datetime_repr(
        datetime.datetime(year, month, last_day, 23, 59, 59))
    return first_moment, last_moment


class MonthlyActivity(object):

    def __init__(self, year, month, count, url):
        self.year = int(year)
        self.month = int(month)
        self.month_name = calendar.month_name[self.month]
        self.count = int(count)
        self.url = url


class BlogSidebar(object):
    implements(ISidebar)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, api):
        activity_list = archive_portlet(self.context, self.request)['archive']
        blog_url = resource_url(self.context, self.request)
        return render(
            'templates/blog_sidebar.pt',
            dict(api=api,
                 activity_list=activity_list,
                 blog_url=blog_url),
            request = self.request,
            )


def archive_portlet(context, request):
    with context._p_jar._storage.ex_cursor() as cursor:
        community = find_community(context)
        community_cond = qbe.sql(context._p_jar, dict(community=community))
        cursor.execute(
            """
            select month, count(*) from (
              select substring(state->>'created' from 1 for 7) as month
              from newt natural join karlex
              where class_name = 'karl.content.models.blog.BlogEntry'
                and """ + community_cond + """
                and newt_can_view(state, %s)
              ) _
            group by month order by month desc
            """, (effective_principals(request),)
            )
        blog = find_interface(context, IBlog)
        return {'archive':
                [MonthlyActivity(
                    year, month, count,
                    request.resource_url(blog,
                                         query={'year': year, 'month': month})
                    )
                 for (year, month, count) in (
                     (month[:4], month[-2:], count)
                     for month, count in cursor
                     )
                 ]}
