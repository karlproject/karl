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

import formish
import schemaish
from validatish import validator

from webob.exc import HTTPFound
from zope.component.event import objectEventNotify
from zope.component import queryUtility

from repoze.bfg.chameleon_zpt import render_template_to_response
from repoze.bfg.security import authenticated_userid
from repoze.bfg.security import has_permission
from repoze.bfg.url import model_url
from repoze.workflow import get_workflow

from repoze.lemonade.content import create_content

from karl.events import ObjectModifiedEvent
from karl.events import ObjectWillBeModifiedEvent

from karl.models.interfaces import ICommunity

from karl.utilities.alerts import Alerts
from karl.utilities.interfaces import IAlerts
from karl.utils import find_interface

from karl.views.api import TemplateAPI

from karl.views.utils import convert_to_script
from karl.views.tags import get_tags_client_data
from karl.views.utils import make_name
from karl.views.tags import set_tags
from karl.views.forms import widgets as karlwidgets
from karl.views.forms import validators as karlvalidators

from karl.content.interfaces import IWiki
from karl.content.interfaces import IWikiPage
from karl.content.views.utils import extract_description

from karl.security.workflow import get_security_states

_wiki_text_help = """You can create a new page by naming it and surrounding
the name with ((double parentheses)). When you save the page, the contents
of the parentheses will have a small + link next to it, which you can click
to create a new page with that name."""

tags_field = schemaish.Sequence(schemaish.String())
text_field = schemaish.String(
    title='Body text',
    description=_wiki_text_help,
    )
sendalert_field = schemaish.Boolean(
    title='Send Alert',
    description='Send email alert to community members?')
security_field = schemaish.String(
    description=('Items marked as private can only be seen by '
                 'members of this community.'))

def redirect_to_front_page(context, request):

    front_page = context['front_page']
    location = model_url(front_page, request)
    return HTTPFound(location=location)


class AddWikiPageFormController(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.workflow = get_workflow(IWikiPage, 'security', context)

    def _get_security_states(self):
        return get_security_states(self.workflow, None, self.request)

    def form_defaults(self):
        defaults = {
            'title':self.request.params.get('title', ''),
            'tags':[],
            'text':'',
            'sendalert':True,
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
                karlvalidators.FolderNameAvailable(self.context),
                )
            )
        fields.append(('title', title_field))
        fields.append(('tags', tags_field))
        fields.append(('text', text_field))
        fields.append(('sendalert', sendalert_field))
        security_states = self._get_security_states()
        if security_states:
            fields.append(('security_state', security_field))
        return fields

    def form_widgets(self, fields):
        widgets = {
            'title':formish.Hidden(empty=''),
            'tags':karlwidgets.TagsAddWidget(),
            'text':karlwidgets.RichTextWidget(empty=''),
            'sendalert':formish.widgets.Checkbox(),
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
        api = TemplateAPI(self.context, self.request)
        head_data = convert_to_script(dict(
            text = dict(enable_wiki_plugin = True),
            ))
        return {'api':api, 'page_title':'Add Wiki Page', 'actions':(),
                'head_data':head_data}

    def handle_cancel(self):
        return HTTPFound(location=model_url(self.context, self.request))

    def handle_submit(self, converted):
        request = self.request
        context = self.context
        workflow = self.workflow
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

class EditWikiPageFormController(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.workflow = get_workflow(IWikiPage, 'security', context)

    def _get_security_states(self):
        return get_security_states(self.workflow, None, self.request)

    def form_defaults(self):
        defaults = {
            'title':self.context.title,
            'tags':[],
            'text':self.context.text,
            }
        if self.workflow is not None:
            defaults['security_state'] = self.workflow.state_of(self.context)
        return defaults

    def form_fields(self):
        fields = []
        title_field = schemaish.String(
            validator=validator.All(
                validator.Length(max=100),
                validator.Required(),
                karlvalidators.FolderNameAvailable(
                    self.context.__parent__,
                    exceptions=(self.context.title,)),
                )
            )
        fields.append(('title', title_field))
        fields.append(('tags', tags_field))
        fields.append(('text', text_field))
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
        api = TemplateAPI(self.context, self.request)
        # prepare client data
        head_data = convert_to_script(dict(
            text = dict(enable_wiki_plugin = True),
            ))
        return {'api':api, 'page_title':'Add Wiki Page', 'actions':(),
                'head_data':head_data}

    def handle_cancel(self):
        return HTTPFound(location=model_url(self.context, self.request))

    def handle_submit(self, converted):
        context = self.context
        request = self.request
        workflow = self.workflow
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
            context.change_title(newtitle)

        # Save the tags on it
        set_tags(context, request, converted['tags'])

        # Modified
        context.modified_by = authenticated_userid(request)
        objectEventNotify(ObjectModifiedEvent(context))

        location = model_url(context, request)
        msg = "?status_message=Wiki%20Page%20edited"
        return HTTPFound(location=location+msg)

