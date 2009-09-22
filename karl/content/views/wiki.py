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

from webob.exc import HTTPFound
from zope.component.event import objectEventNotify
from zope.component import queryUtility

from formencode import Invalid

from repoze.bfg.chameleon_zpt import render_template_to_response
from repoze.bfg.security import authenticated_userid
from repoze.bfg.security import has_permission
from repoze.bfg.url import model_url
from repoze.workflow import get_workflow
from repoze.enformed import FormSchema

from repoze.lemonade.content import create_content

from karl.events import ObjectModifiedEvent
from karl.events import ObjectWillBeModifiedEvent

from karl.models.interfaces import ICommunity

from karl.utilities.alerts import Alerts
from karl.utilities.interfaces import IAlerts
from karl.utils import find_interface

from karl.views.api import TemplateAPI
from karl.views import baseforms

from karl.views.utils import convert_to_script
from karl.views.tags import get_tags_client_data
from karl.views.utils import make_name
from karl.views.tags import set_tags
from karl.views.form import render_form_to_response
from karl.views.baseforms import security_state as security_state_field

from karl.content.interfaces import IWiki
from karl.content.interfaces import IWikiPage
from karl.content.views.utils import extract_description

from karl.security.workflow import get_security_states

def redirect_to_front_page(context, request):

    front_page = context['front_page']
    location = model_url(front_page, request)
    return HTTPFound(location=location)

def add_wikipage_view(context, request):

    tags_list = request.POST.getall('tags')
    form = AddWikiPageForm(tags_list = tags_list)
    workflow = get_workflow(IWikiPage, 'security', context)

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
            wikipage = create_content(
                IWikiPage,
                converted['title'],
                converted['text'],
                extract_description(converted['text']),
                authenticated_userid(request),
                )

            name = make_name(context, converted['title'])
            context[name] = wikipage

            if workflow is not None:
                workflow.initialize(wikipage)
                if 'security_state' in converted:
                    workflow.transition_to_state(wikipage,
                                                 request,
                                                 converted['security_state'])
                                             

            # Save the tags on it.
            set_tags(wikipage, request, converted['tags'])

            if converted['sendalert']:
                alerts = queryUtility(IAlerts, default=Alerts())
                alerts.emit(wikipage, request)

            msg = '?status_message=Wiki%20Page%20created'
            location = model_url(wikipage, request) + msg
            return HTTPFound(location=location)

        except Invalid, e:
            fielderrors = e.error_dict
            fill_values = form.convert(request.POST)
    else:
        fielderrors = {}
        if workflow is None:
            security_state = ''
        else:
            security_state = workflow.initial_state
        fill_values = dict(security_state=security_state)

    # provide client data for rendering current tags in the tagbox.
    if 'form.submitted' in request.POST:
        # We arrived here because the form is invalid.
        tagbox_records = [dict(tag=tag) for tag in form.formdata.getall('tags')]
    else:
        # Since this is a new entry, we start with no tags.
        tagbox_records = []

    client_json_data = convert_to_script(dict(
        tags_field = dict(
            # There is no document right now, so we leave docid empty.
            # This will cause the count links become non-clickable.
            records = tagbox_records,
            ),
        text = dict(
            # This is the simplest way to pass information
            # to the tinyMCE widget.
            enable_wiki_plugin = True,
            ),
    ))

    # Wiki pages get passed a value for the title field in the query
    # string as part of clicking on the + from the referrer.
    title = request.params.get('title', False)
    if title is False:
        raise ValueError, "URL must have a title passed into it"

    fill_values['title'] = title

    # Render the form and shove some default values in
    page_title = 'Add "' + title + '"'
    api = TemplateAPI(context, request, page_title)

    return render_form_to_response(
        'templates/add_wikipage.pt',
        form,
        fill_values,
        post_url=request.url,
        formfields=api.formfields,
        fielderrors=fielderrors,
        api=api,
        head_data=client_json_data,
        labels={'text': 'Hello There'},
        security_states = security_states,
        )


def show_wikipage_view(context, request):

    is_front_page = (context.__name__ == 'front_page')
    if is_front_page:
        community = find_interface(context, ICommunity)
        page_title = '%s Community Wiki Page' % community.title
        backto = False
    else:
        page_title = context.title
        backto = {
            'href': model_url(context.__parent__, request),
            'title': context.__parent__.title,
            }

    actions = []
    if has_permission('create', context, request):
        actions.append(
            ('Edit', 'edit.html'),
            )
        if not is_front_page:
            actions.append(
                ('Delete', 'delete.html'),
                )

    api = TemplateAPI(context, request, page_title)

    client_json_data = convert_to_script(dict(
        tagbox = get_tags_client_data(context, request),
        ))

    wiki = find_interface(context, IWiki)
    feed_url = model_url(wiki, request, "atom.xml")
    return render_template_to_response(
        'templates/show_wikipage.pt',
        api=api,
        actions=actions,
        head_data=client_json_data,
        feed_url=feed_url,
        backto=backto,
        )

def edit_wikipage_view(context, request):

    tags_list = request.POST.getall('tags')
    form = EditWikiPageForm(tags_list = tags_list)
    workflow = get_workflow(IWikiPage, 'security', context)

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
            if workflow is not None:
                if 'security_state' in converted:
                    workflow.transition_to_state(context, request,
                                                 converted['security_state'])

            context.text = converted['text']
            context.description = extract_description(converted['text'])
            newtitle = converted['title']
            if newtitle != context.title:
                # change_title changes the page's title but also fixes
                # up referent links in other pages in the wiki
                try:
                    context.change_title(newtitle)
                except ValueError, why:
                    # the title may already be the title of an existing page
                    msg = str(why)
                    raise Invalid(msg, newtitle, None,
                                  error_dict={'title':msg})

            # Save the tags on it
            set_tags(context, request, converted['tags'])

            # Modified
            context.modified_by = authenticated_userid(request)
            objectEventNotify(ObjectModifiedEvent(context))

            location = model_url(context, request)
            msg = "?status_message=Wiki%20Page%20edited"
            return HTTPFound(location=location+msg)

        except Invalid, e:
            fielderrors = e.error_dict
            fill_values = form.convert(request.POST)
    else:
        fielderrors = {}
        if workflow is None:
            security_state = ''
        else:
            security_state = workflow.state_of(context)
        fill_values = dict(text=context.text,
                           title=context.title,
                           security_state = security_state)

    # prepare client data
    client_json_data = convert_to_script(dict(
        tags_field = get_tags_client_data(context, request),
        # This is the simplest way to pass information
        # to the tinyMCE widget.
        text = dict(enable_wiki_plugin = True),
        ))

    # Render the form and shove some default values in
    page_title = 'Edit ' + context.title
    api = TemplateAPI(context, request, page_title)

    return render_form_to_response(
        'templates/edit_wikipage.pt',
        form,
        fill_values,
        post_url=request.url,
        formfields=api.formfields,
        fielderrors=fielderrors,
        api=api,
        help={'text': _wiki_text_help,},
        head_data=client_json_data,
        security_states = security_states,
        )

class AddWikiPageForm(FormSchema):
    title = baseforms.title
    tags = baseforms.tags
    text = baseforms.text
    sendalert = baseforms.sendalert

class EditWikiPageForm(FormSchema):
    title = baseforms.title
    tags = baseforms.tags
    text = baseforms.text

_wiki_text_help = """You can create a new page by naming it and surrounding
the name with ((double parentheses)). When you save the page, the contents
of the parentheses will have a small + link next to it, which you can click
to create a new page with that name."""
