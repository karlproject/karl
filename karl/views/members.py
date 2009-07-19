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

"""Community membership views, both for browsing and managing.

Includes invitations, per-user preferences on alerts, etc.
"""

import transaction

from email.Message import Message
from formencode import Invalid
from webob import Response
from simplejson import JSONEncoder

from webob.exc import HTTPFound
from zope.component import getUtility
from zope.component import queryMultiAdapter

from repoze.bfg.chameleon_zpt import render_template_to_response
from repoze.bfg.chameleon_zpt import get_template
from repoze.bfg.security import has_permission
from repoze.bfg.security import effective_principals
from repoze.bfg.traversal import model_path
from repoze.bfg.traversal import find_interface
from repoze.bfg.url import model_url
from repoze.enformed import FormSchema

from repoze.lemonade.content import create_content
from repoze.sendmail.interfaces import IMailDelivery

from karl.views.api import TemplateAPI
from karl.views.batch import get_catalog_batch
from karl.views.form import render_form_to_response

from karl.models.interfaces import ICommunity
from karl.models.interfaces import IProfile
from karl.models.interfaces import ICatalogSearch
from karl.models.interfaces import IInvitation

from karl.security.interfaces import ISecurityWorkflow
from karl.utilities.interfaces import IRandomId

from karl.utils import find_profiles
from karl.utils import find_users
from karl.utils import get_setting

from karl.views import baseforms
from karl.views.interfaces import IInvitationBoilerplate
from karl.views.utils import handle_photo_upload


def _get_manage_actions(community, request):

    # Filter the actions based on permission in the **community**
    actions = []
    if has_permission('moderate', community, request):
        actions.append(('Manage Members', 'manage.html'))
        actions.append(('Add Existing', 'add_existing.html'))
        actions.append(('Invite New', 'invite_new.html'))

    return actions

def _get_common_email_info(community, community_href):
    info = {}
    info['system_name'] = get_setting(community, 'system_name')
    info['system_email_domain'] = get_setting(community,
                                              'system_email_domain')
    info['from_name'] = '%s invitation' % info['system_name']
    info['from_email'] = 'invitation@%s' % info['system_email_domain']
    info['c_title'] = community.title
    info['c_description'] = community.description
    info['c_href'] = community_href
    info['mfrom'] = '%s <%s>' % (info['from_name'], info['from_email'])

    return info

def _member_profile_batch(context, request):
    community = find_interface(context, ICommunity)
    member_names = community.member_names
    profiles_path = model_path(find_profiles(context))
    batch = get_catalog_batch(
        context, request,
        batch_size = 12,
        interfaces = [IProfile],
        path={'query': profiles_path, 'depth': 1},
        allowed={'query': effective_principals(request), 'operator': 'or'},
        name = list(member_names),
        sort_index='lastfirst',
        )
    return batch

def show_members_view(context, request):
    """Default view of community members (with/without pictures)."""

    page_title = 'Community Members'
    api = TemplateAPI(context, request, page_title)

    # Filter the actions based on permission in the **community**
    community = find_interface(context, ICommunity)
    actions = _get_manage_actions(community, request)

    # Did we get the "show pictures" flag?
    hp = request.params.has_key('hide_pictures')
    mu = model_url(context, request)
    submenu = [
        {'label': 'Show Pictures',
         'href': mu, 'make_link': hp},
        {'label': 'Hide Pictures',
         'href': mu + '?hide_pictures', 'make_link': not(hp)},
        ]

    profiles = find_profiles(context)
    member_batch = _member_profile_batch(context, request)
    member_entries = member_batch['entries']
    moderator_names = community.moderator_names

    member_info = []
    for i in range(len(member_entries)):
        derived = {}
        entry = member_entries[i]
        derived['title'] = entry.title
        derived['href'] = model_url(entry, request)
        derived['position'] = entry.position
        derived['organization'] = entry.organization
        derived['phone'] = entry.phone
        derived['department'] = entry.department
        derived['email'] = entry.email
        derived['city'] = entry.location

        photo = entry.get_photo()
        if photo is not None:
            derived['photo_url'] = model_url(photo, request)
        else:
            derived['photo_url'] = api.static_url + "/images/defaultUser.gif"

        derived['is_moderator'] = entry.__name__ in moderator_names
        # Chameleon's tal:repeat and repeat variable support for
        # things like index is pretty iffy.  Fix the entry info to
        # supply the CSS class information.
        derived['css_class'] = 'photoProfile'
        if derived['is_moderator']:
            derived['css_class'] += ' moderator'
        member_info.append(derived)

    moderator_info = []
    profiles = find_profiles(context)
    for moderator_name in moderator_names:
        if moderator_name in profiles:
            derived = {}
            profile = profiles[moderator_name]
            if not has_permission('view', profile, request):
                continue
            name = profile.__name__
            derived['title'] = profile.title
            derived['href'] = model_url(profile, request)
            moderator_info.append(derived)

    return render_template_to_response(
        'templates/show_members.pt',
        api=api,
        actions=actions,
        submenu=submenu,
        moderators=moderator_info,
        members=member_info,
        batch_info=member_batch,
        hide_pictures=hp,
        )


from formencode import Schema
from formencode import variabledecode
from formencode import ForEach

class ManageMembersEntry(Schema):
    id = baseforms.profile_id
    is_moderator = baseforms.is_moderator
    resend_info = baseforms.resend_info
    remove = baseforms.remove_entry

class ManageMembersForm(FormSchema):
    pre_validators = [variabledecode.NestedVariables()]
    moderators = ForEach(ManageMembersEntry())
    members = ForEach(ManageMembersEntry())
    invitations = ForEach(ManageMembersEntry())

def _send_moderators_changed_email(community,
                                   community_href,
                                   new_moderators,
                                   old_moderators,
                                   cur_moderators,
                                   prev_moderators):
    info = _get_common_email_info(community, community_href)
    subject_fmt = 'Change in moderators for %s'
    subject = subject_fmt % info['c_title']
    body_template = get_template('templates/email_moderators_changed.pt')

    profiles = find_profiles(community)
    all_moderators = cur_moderators | prev_moderators
    to_profiles = [profiles[name] for name in all_moderators]
    to_addrs = ["%s <%s>" % (p.title, p.email) for p in to_profiles]

    mailer = getUtility(IMailDelivery)
    msg = Message()
    msg['From'] = info['mfrom']
    msg['To'] = ",".join(to_addrs)
    msg['Subject'] = subject
    body = body_template(
        system_name=info['system_name'],
        community_href=info['c_href'],
        community_name=info['c_title'],
        new_moderators=[profiles[name].title for name in new_moderators],
        old_moderators=[profiles[name].title for name in old_moderators],
        cur_moderators=[profiles[name].title for name in cur_moderators],
        prev_moderators=[profiles[name].title for name in prev_moderators]
        )

    if isinstance(body, unicode):
        body = body.encode("UTF-8")

    msg.set_payload(body, "UTF-8")
    msg.set_type('text/html')
    message = msg.as_string()
    mailer.send(info['mfrom'], to_addrs, message)


def manage_members_view(context, request):
    """ Moderators managing the list of members"""

    page_title = 'Manage Community Members'
    api = TemplateAPI(context, request, page_title)

    # Filter the actions based on permission in the **community**
    community = find_interface(context, ICommunity)
    community_href = model_url(community, request)
    actions = _get_manage_actions(community, request)

    form = ManageMembersForm()
    if 'form.cancel' in request.params:
        return HTTPFound(location=model_url(context, request))

    profiles = find_profiles(community)
    status_message=None
    results = []
    if 'form.submitted' in request.params:
        try:
            converted = form.validate(request.POST)
            c_moderators = converted['moderators']
            c_members = converted['members']
            c_invitations = converted['invitations']

            # Now process any changes.  These are highly specific, so
            # let's make sure the flow of control is obvious.
            # Invariant: Don't allow removal of the last moderator.
            prev_moderators = community.moderator_names.copy()
            users = find_users(context)
            for action in c_moderators:
                if action['remove']:
                    name = action['id']
                    users.remove_group(name, community.moderators_group_name)
                    users.remove_group(name, community.members_group_name)
                    profile = profiles[name]
                    results.append('Removed moderator %s' % profile.title)

                elif not action['is_moderator']:
                    if not action['is_moderator']:
                        name = action['id']
                        users.remove_group(name,community.moderators_group_name)
                        profile = profiles[name]
                        results.append('%s is no longer a moderator' %
                                       profile.title)

            for action in c_members:
                name = action['id']
                if action['remove']:
                    users.remove_group(name, community.members_group_name)
                    profile = profiles[name]
                    results.append('Removed member %s' % profile.title)
                elif name not in community.moderator_names:
                    if action['is_moderator']:
                        users.add_group(name, community.moderators_group_name)
                        profile = profiles[name]
                        results.append('%s is now a moderator' % profile.title)

            for action in c_invitations:
                name = action['id']
                invitation = context.get(name)
                if IInvitation.providedBy(invitation):
                    if action['remove']:
                        del context[name]
                    elif action['resend_info']:
                        _send_invitation_email(request, community, community_href,
                                               invitation)

            if not community.moderator_names:
                raise Invalid(
                    "Must leave at least one moderator for community.",
                    None, None
                )

            cur_moderators = community.moderator_names
            new_moderators = cur_moderators - prev_moderators
            old_moderators = prev_moderators - cur_moderators
            if new_moderators or old_moderators:
                _send_moderators_changed_email(community, community_href,
                                               new_moderators, old_moderators,
                                               cur_moderators, prev_moderators)

            status_message = 'Membership information changed'
            location = model_url(context, request, "manage.html",
                                 query={"status_message": status_message})
            return HTTPFound(location=location)

        except Invalid, e:
            # Since we've already monkeyed with our model graph, we need
            # to abort transaction to undo changes.
            transaction.manager.abort()
            location = model_url(context, request, "manage.html",
                                 query={"error_message": e.msg})
            return HTTPFound(location=location)

    # Assemble the grid data needed for the ZPT
    moderators_info = []
    members_info = []
    invitations_info = []

    def profile_sortkey(profile):
        return '%s, %s' % (profile.lastname, profile.firstname)
    def get_sortkey(info):
        return info['sortkey']

    for mod_name in community.moderator_names:
        profile = profiles[mod_name]
        moderators_info.append({
            'sortkey': profile_sortkey(profile),
            'id': mod_name, 'title': profile.title, 'is_moderator': True,
            'resend_info': False, 'remove': False,
            })
    moderators_info.sort(key=get_sortkey)

    for mem_name in community.member_names:
        if mem_name not in community.moderator_names:
            profile = profiles[mem_name]
            members_info.append({
                'sortkey': profile_sortkey(profile),
                'id': mem_name, 'title': profile.title, 'is_moderator': False,
                'resend_info': False, 'remove': False,
                })
    members_info.sort(key=get_sortkey)

    for invite_name, invitation in context.items():
        if IInvitation.providedBy(invitation):
            invitations_info.append({
                'sortkey': invitation.email,
                'id':invite_name, 'title': invitation.email,
                'is_moderator': False, 'resend_info': False, 'remove': False,
                })
    invitations_info.sort(key=get_sortkey)

    entries = {
        'moderators': moderators_info,
        'members': members_info,
        'invitations':invitations_info,
        }

    api.status_message = status_message
    return render_template_to_response(
        'templates/manage_members.pt',
        api=api,
        actions=actions,
        post_url=request.url,
        formfields=get_template('templates/formfields.pt'),
        entries=entries,
        results=results,
        fielderrors={},
        )

class AddExistingUserForm(FormSchema):
    users = baseforms.users
    text = baseforms.text

def _send_aeu_emails(community, community_href, profiles, text):
    # To make reading the add_existing_user_view easier, move the mail
    # delivery part here.

    info = _get_common_email_info(community, community_href)
    subject_fmt = 'You have been added to the %s community'
    subject = subject_fmt % info['c_title']
    body_template = get_template('templates/email_add_existing.pt')
    html_body = text

    mailer = getUtility(IMailDelivery)
    for profile in profiles:
        to_email = profile.email

        msg = Message()
        msg['From'] = info['mfrom']
        msg['To'] = to_email
        msg['Subject'] = subject
        body = body_template(
            system_name=info['system_name'],
            community_href=info['c_href'],
            community_name=info['c_title'],
            community_description=info['c_description'],
            personal_message=html_body,
            )

        if isinstance(body, unicode):
            body = body.encode("UTF-8")

        msg.set_payload(body, "UTF-8")
        msg.set_type('text/html')
        message = msg.as_string()
        mailer.send(info['mfrom'], [to_email,], message)


def add_existing_user_view(context, request):
    """ Add an existing KARL3 user. """

    system_name = get_setting(context, 'system_name')

    community = find_interface(context, ICommunity)
    actions = _get_manage_actions(community, request)
    profiles = find_profiles(context)

    fieldwidgets = get_template('templates/formfields.pt')
    usernames=request.POST.getall('users')
    form = AddExistingUserForm(usernames = usernames, profiles=profiles)

    # Handle form submission
    if 'form.cancel' in request.params:
        return HTTPFound(location=model_url(context, request))

    if 'form.submitted' in request.params:
        try:
            converted = form.validate(request.POST)
            return _add_existing_users(context, community, converted['users'],
                                       converted['text'], request)
        except Invalid, e:
            fielderrors = e.error_dict
            fill_values = form.convert(request.POST)
    else:
        fielderrors = {}
        fill_values = {}

    # Handle userid passed in via GET request
    # Moderator would get here by clicking a link in an email to grant a
    # user's request to join this community.
    add_user_id = request.params.get("user_id", None)
    if add_user_id is not None:
        profile = profiles.get(add_user_id, None)
        if profile is not None:
            return _add_existing_users(context, community, [profile,],
                                       "", request)

    # Render the form and shove some default values in
    page_title = 'Add Existing %s Users' % system_name
    api = TemplateAPI(context, request, page_title)

    return render_form_to_response(
        'templates/add_existing_user.pt',
        form,
        fill_values,
        post_url=request.url,
        formfields=fieldwidgets,
        fielderrors=fielderrors,
        api=api,
        system_name=system_name,
        community_name=community.title,
        actions=actions,
        )

def _add_existing_users(context, community, profiles, text, request):
    users = find_users(community)
    for profile in profiles:
        group_name = community.members_group_name
        user_name = profile.__name__
        users.add_group(user_name, group_name)

    # Generate HTML and text mail messages and send a mail for
    # each user added to the community.
    community_href = model_url(community, request)
    _send_aeu_emails(community, community_href, profiles, text)

    # We delivered invitation messages to each user.  Redirect to
    # Manage Members with a status message.
    n = len(profiles)
    if n == 1:
        msg = 'One member added and email sent.'
    else:
        fmt = '%s members added and emails sent.'
        msg = fmt % len(profiles)
    location = model_url(context, request, 'manage.html',
                         query={'status_message': msg})
    return HTTPFound(location=location)

class AcceptInvitationForm(FormSchema):
    username = baseforms.username
    password = baseforms.password
    password_confirm = baseforms.password_confirm
    firstname = baseforms.firstname
    lastname = baseforms.lastname
    phone = baseforms.phone
    extension = baseforms.extension
    organization = baseforms.organization
    country = baseforms.country
    location = baseforms.location
    department = baseforms.department
    position = baseforms.position
    website = baseforms.website
    languages = baseforms.languages
    biography = baseforms.biography
    photo = baseforms.photo
    terms_and_conditions = baseforms.terms_and_conditions
    accept_privacy_policy = baseforms.accept_privacy_policy
    chained_validators = baseforms.chained_validators

def _send_ai_email(community, community_href, username, profile):
    """Send email to user who has accepted a community invitation.
    """
    info = _get_common_email_info(community, community_href)
    subject_fmt = 'Thank you for joining the %s community'
    subject = subject_fmt % info['c_title']
    body_template = get_template('templates/email_accept_invitation.pt')

    mailer = getUtility(IMailDelivery)
    msg = Message()
    msg['From'] = info['mfrom']
    msg['To'] = profile.email
    msg['Subject'] = subject
    body = body_template(
        community_href=info['c_href'],
        community_name=info['c_title'],
        community_description=info['c_description'],
        username=username,
        )

    if isinstance(body, unicode):
        body = body.encode("UTF-8")

    msg.set_payload(body, "UTF-8")
    msg.set_type('text/html')
    message = msg.as_string()
    mailer.send(info['mfrom'], [profile.email,], message)


def accept_invitation_view(context, request):
    """ Process invitation, add KARL user, add member to community """
    assert IInvitation.providedBy(context), \
           "Context is expected to be an IInvitation."

    profiles = find_profiles(context)
    system_name = get_setting(context, 'system_name')
    min_pw_length = get_setting(context, 'min_pw_length')
    community = find_interface(context, ICommunity)
    community_name = community.title

    fieldwidgets = get_template('templates/formfields.pt')
    form = AcceptInvitationForm(profiles=profiles, min_pw_length=min_pw_length)

    if 'form.cancel' in request.params:
        return HTTPFound(location=model_url(context, request))

    if 'form.submitted' in request.params:
        try:
            converted = form.validate(request.POST)
            users = find_users(context)
            username = converted['username']
            password = converted['password']
            community_href = model_url(community, request)
            groups = [ community.members_group_name ]
            users.add(username, username, password, groups)
            plugin = request.environ['repoze.who.plugins']['auth_tkt']
            identity = {'repoze.who.userid':username}
            remember_headers = plugin.remember(request.environ, identity)
            profile = create_content(
                IProfile,
                firstname=converted['firstname'],
                lastname=converted['lastname'],
                email=context.email,
                phone=converted['phone'],
                extension=converted['extension'],
                department=converted['department'],
                position=converted['position'],
                organization=converted['organization'],
                location=converted['location'],
                country=converted['country'],
                website=converted['website'],
                languages=converted['languages']
                )
            profiles[username] = profile
            ISecurityWorkflow(profile).setInitialState()
            handle_photo_upload(profile, converted, thumbnail=True)

            del context.__parent__[context.__name__]
            url = model_url(community, request,
                            query={'status_message':'Welcome!'})
            _send_ai_email(community, community_href, username, profile)
            return HTTPFound(headers=remember_headers, location=url)

        except Invalid, e:
            fielderrors = e.error_dict
            fill_values = form.convert(request.POST)
            try:
                del fill_values['photo'] # rendering cant deal with photo
            except KeyError:
                pass
    else:
        fielderrors = {}
        # hack to make chained validators work
        fill_values = {'password':'', 'password_confirm':''}

    # Get text for two dialogs.  We get this from content in
    # /offices/files, named with a special name.
    terms_text = "<div><h1>Terms and Conditions</h1><p>text</p></div>"
    privacy_text = "<div><h1>Privacy</h1><p>text</p></div>"
    r = queryMultiAdapter((context, request), IInvitationBoilerplate)
    if r is not None:
        terms_text = r.terms_and_conditions
        privacy_text = r.privacy_statement

    # Render the form and shove some default values in
    page_title = 'Accept Invitation'
    api = TemplateAPI(context, request, page_title)
    photo = {}
    photo["url"] =  api.app_url + "/static/images/defaultUser.gif"
    photo["may_delete"] = False

    return render_form_to_response(
        'templates/accept_invitation.pt',
        form,
        fill_values,
        post_url=request.url,
        formfields=fieldwidgets,
        fielderrors=fielderrors,
        terms_text=terms_text,
        privacy_text=privacy_text,
        photo=photo,
        api=api,
        system_name=system_name,
        community_name=community_name,
        )

class InviteNewUsersForm(FormSchema):
    email_addresses = baseforms.email_addresses
    text = baseforms.text

def invite_new_user_view(context, request):
    """ Invite a new user to join KARL and thus this community. """
    system_name = get_setting(context, 'system_name')

    community = find_interface(context, ICommunity)
    community_href = model_url(community, request)
    actions = _get_manage_actions(community, request)

    fieldwidgets = get_template('templates/formfields.pt')
    form = InviteNewUsersForm()

    ninvited = nadded = nignored = 0

    if 'form.cancel' in request.params:
        return HTTPFound(location=model_url(context, request))

    if 'form.submitted' in request.params:
        try:
            converted = form.validate(request.POST)
            addresses = converted['email_addresses']
            random_id = getUtility(IRandomId)
            html_body = converted['text']
            members = community.member_names | community.moderator_names

            search = ICatalogSearch(context)

            for email_address in addresses:
                # Check for existing members
                total, docids, resolver = search(
                    email=email_address.lower(),
                    interfaces=[IProfile,],
                    )

                if total:
                    # User is already a member of Karl
                    profile = resolver(docids[0])

                    if profile.__name__ in members:
                        # User is a member of this community, do nothing
                        nignored += 1

                    else:
                        # User is in Karl but not in this community--just add
                        # them to the community as though we had used the
                        # add existing user form.
                        _add_existing_users(context, community, [profile,],
                                            html_body, request)
                        nadded += 1

                else:
                    # Invite new user to Karl
                    invitation = create_content(
                        IInvitation,
                        email_address,
                        html_body
                    )
                    while 1:
                        name = random_id()
                        if name not in context:
                            context[name] = invitation
                            break

                    _send_invitation_email(request, community, community_href,
                                           invitation)
                    ninvited += 1

            status = ''
            if ninvited:
                if ninvited == 1:
                    status = 'One user invited.  '
                else:
                    status = '%d users invited.  ' % ninvited

            if nadded:
                if nadded == 1:
                    status += 'One existing Karl user added to community.  '
                else:
                    status += ('%d existing Karl users added to community.  '
                               % nadded)
            if nignored:
                if nignored == 1:
                    status += 'One user already member.'
                else:
                    status += '%d users already members.' % nignored

            location = model_url(context, request, 'manage.html',
                                 query={'status_message': status})
            return HTTPFound(location=location)

        except Invalid, e:
            fielderrors = e.error_dict
            fill_values = form.convert(request.POST)
    else:
        fill_values = {}
        fielderrors = {}

    page_title = 'Invite New KARL Users'
    api = TemplateAPI(context, request, page_title)

    return render_form_to_response(
        'templates/invite_new_user.pt',
        form,
        fill_values,
        post_url=request.url,
        formfields=fieldwidgets,
        fielderrors=fielderrors,
        api=api,
        actions=actions,
        )

def _send_invitation_email(request, community, community_href, invitation):
    mailer = getUtility(IMailDelivery)
    info = _get_common_email_info(community, community_href)
    subject_fmt = 'Please join the %s community at %s'
    info['subject'] = subject_fmt % (info['c_title'],
                                     info['system_name'])
    body_template = get_template('templates/email_invite_new.pt')

    msg = Message()
    msg['From'] = info['mfrom']
    msg['To'] = invitation.email
    msg['Subject'] = info['subject']
    body = body_template(
        system_name=info['system_name'],
        community_href=info['c_href'],
        community_name=info['c_title'],
        community_description=info['c_description'],
        personal_message=invitation.message,
        invitation_url=model_url(invitation.__parent__, request,
                                 invitation.__name__)
        )

    if isinstance(body, unicode):
        body = body.encode("UTF-8")

    msg.set_payload(body, "UTF-8")
    msg.set_type('text/html')
    message = msg.as_string()
    mailer.send(info['mfrom'], [invitation.email,], message)

def jquery_member_search_view(context, request):
    prefix = request.params['val'].lower()
    community = find_interface(context, ICommunity)
    member_names = community.member_names
    moderator_names = community.moderator_names
    community_member_names = member_names.union(moderator_names)
    query = dict(
        member_name='%s*' % prefix,
        sort_index='title',
        limit=20,
        )
    searcher = ICatalogSearch(context)
    total, docids, resolver = searcher(**query)
    profiles = filter(None, map(resolver, docids))
    records = [dict(
                id = profile.__name__,
                text = profile.firstname + ' ' + profile.lastname,
                )
            for profile in profiles
            if profile.__name__ not in community_member_names ]
    result = JSONEncoder().encode(records)
    return Response(result, content_type="application/x-json")


